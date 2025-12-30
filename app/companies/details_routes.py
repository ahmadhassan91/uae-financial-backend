"""Companies Details API routes for CSV upload and customer profile management."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
from datetime import datetime

from ..database import get_db
from ..models import CompanyDetails, CompanyCustomerProfile, User
from ..auth.dependencies import get_current_admin_user
from .schemas import (
    CompanyDetailsResponse, CompanyCustomerProfileResponse, 
    CSVUploadResponse, CompanyListResponse
)

router = APIRouter(prefix="/companies-details", tags=["companies-details"])


@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_companies_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload a CSV file containing company details."""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read and parse CSV file
        contents = await file.read()
        csv_reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))
        
        uploaded_companies = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 because header is row 1
            try:
                # Validate required fields - only Company Name is required now
                if not row.get('Company Name'):
                    errors.append(f"Row {row_num}: Missing required field (Company Name)")
                    continue
                
                # Create company details with default values for optional fields
                company = CompanyDetails(
                    company_name=row['Company Name'].strip(),
                    company_email=row.get('Email', '').strip() or 'no-email@example.com',
                    contact_person=row.get('Contact', '').strip() or 'Not specified',
                    phone_number=row.get('Phone', '').strip() if row.get('Phone') else None,
                    additional_details=row.get('Details', '').strip() if row.get('Details') else None,
                    uploaded_by=current_user.id
                )
                
                db.add(company)
                db.flush()  # Get the ID without committing
                
                uploaded_companies.append(company)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        # Commit all successful additions
        db.commit()
        
        # Prepare response
        company_responses = []
        for company in uploaded_companies:
            company_responses.append(CompanyDetailsResponse.from_orm(company))
        
        return CSVUploadResponse(
            message=f"Successfully uploaded {len(uploaded_companies)} companies",
            companies_uploaded=len(uploaded_companies),
            companies=company_responses
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")


@router.get("/companies", response_model=CompanyListResponse)
async def get_uploaded_companies(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of uploaded companies with optional search."""
    
    query = db.query(CompanyDetails)
    
    if search:
        query = query.filter(
            CompanyDetails.company_name.ilike(f"%{search}%")
        )
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    company_responses = [CompanyDetailsResponse.from_orm(company) for company in companies]
    
    return CompanyListResponse(
        companies=company_responses,
        total=total
    )


@router.get("/public-companies")
async def get_public_companies(
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(CompanyDetails)
    
    if search:
        query = query.filter(
            CompanyDetails.company_name.ilike(f"%{search}%")
        )
    
    companies = (
        query
        .order_by(CompanyDetails.company_name)
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": company.id,
            "name": company.company_name
        }
        for company in companies
    ]


@router.post("/customer-profile", response_model=CompanyCustomerProfileResponse)
async def create_customer_profile(
    company_id: int = Form(...),
    full_name: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    emirate: str = Form(...),
    children: str = Form(...),
    employment_status: str = Form(...),
    household_income: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a customer profile linked to a company."""
    
    # Validate company exists
    company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Parse date of birth
        dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
        
        # Create customer profile
        customer_profile = CompanyCustomerProfile(
            company_id=company_id,
            full_name=full_name,
            date_of_birth=dob,
            gender=gender,
            nationality=nationality,
            emirate=emirate,
            children=children,
            employment_status=employment_status,
            household_income=household_income,
            email=email,
            mobile_number=mobile_number,
            created_by=current_user.id
        )
        
        db.add(customer_profile)
        db.commit()
        db.refresh(customer_profile)
        
        return CompanyCustomerProfileResponse.from_orm(customer_profile)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating customer profile: {str(e)}")


@router.get("/customer-profiles", response_model=List[CompanyCustomerProfileResponse])
async def get_customer_profiles(
    company_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get customer profiles, optionally filtered by company."""
    
    query = db.query(CompanyCustomerProfile)
    
    if company_id:
        query = query.filter(CompanyCustomerProfile.company_id == company_id)
    
    profiles = query.offset(skip).limit(limit).all()
    
    return [CompanyCustomerProfileResponse.from_orm(profile) for profile in profiles]


@router.get("/search-companies")
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Search companies by name for autocomplete."""
    
    companies = db.query(CompanyDetails).filter(
        CompanyDetails.company_name.ilike(f"%{q}%")
    ).limit(limit).all()
    
    return [
        {
            "id": company.id,
            "name": company.company_name,
            "email": company.company_email,
            "contact": company.contact_person
        }
        for company in companies
    ]


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a company and all its associated customer profiles."""
    
    company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Delete associated customer profiles first
        db.query(CompanyCustomerProfile).filter(
            CompanyCustomerProfile.company_id == company_id
        ).delete()
        
        # Delete the company
        db.delete(company)
        db.commit()
        
        return {"message": "Company and associated profiles deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting company: {str(e)}")
