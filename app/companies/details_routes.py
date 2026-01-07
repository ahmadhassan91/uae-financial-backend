"""Companies Details API routes for CSV upload and customer profile management."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import os
from datetime import datetime

from ..database import get_db
from ..models import CompanyDetails, CompanyCustomerProfile, User
from ..auth.dependencies import get_current_admin_user, get_current_user
from ..middleware.rate_limiter import limiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from .schemas import (
    CompanyDetailsResponse, CompanyCustomerProfileResponse, 
    CSVUploadResponse, CompanyListResponse
)

router = APIRouter(prefix="/companies-details", tags=["companies-details"])


@router.get("/module-status")
async def get_companies_module_status():
    """Get the current status of the companies module (enabled/disabled)."""
    # Check environment variable directly for dynamic updates
    enabled = os.environ.get("COMPANIES_MODULE_ENABLED", "true").lower() == "true"
    return {
        "enabled": enabled,
        "message": "Companies module is enabled" if enabled else "Companies module is disabled"
    }


@router.put("/module-status")
async def update_companies_module_status(
    enabled: bool = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update the companies module status (admin only).
    Note: This sets an environment variable. For permanent change, update Heroku config vars.
    """
    os.environ["COMPANIES_MODULE_ENABLED"] = str(enabled).lower()
    
    # Update the settings object directly for immediate effect
    from app.config import settings
    # Note: Pydantic settings are immutable, so we modify the env var
    # The change will take effect on next settings access or app restart
    
    return {
        "enabled": enabled,
        "message": f"Companies module {'enabled' if enabled else 'disabled'} successfully. Note: Restart the app or update Heroku config vars for permanent change."
    }


@router.post("/create-from-other", response_model=CompanyDetailsResponse)
async def create_company_from_other(
    company_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Can be any user, not just admin
):
    """Create a company when user selects 'Other' and enters custom company name."""
    
    print(f"🔧 [DEBUG] Creating company from 'Other': {company_name}")
    
    if not company_name or not company_name.strip():
        raise HTTPException(status_code=400, detail="Company name is required")
    
    try:
        # Check if company already exists
        existing_company = db.query(CompanyDetails).filter(CompanyDetails.company_name == company_name.strip()).first()
        
        if existing_company:
            print(f"🔧 [DEBUG] Company already exists: {existing_company.company_name}")
            return {
                "id": str(existing_company.id),
                "company_name": existing_company.company_name,
                "company_email": existing_company.company_email,
                "contact_person": existing_company.contact_person,
                "phone_number": existing_company.phone_number,
                "additional_details": existing_company.additional_details,
                "created_at": existing_company.created_at.isoformat(),
                "updated_at": existing_company.updated_at.isoformat() if existing_company.updated_at else None,
                "is_active": existing_company.is_active,
                "uploaded_by": existing_company.uploaded_by
            }
        else:
            # Create new company with minimal info
            company = CompanyDetails(
                company_name=company_name.strip(),
                company_email=None,
                contact_person=None,
                phone_number=None,
                additional_details="Created via user submission (Other option)",
                uploaded_by=current_user.id
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
            print(f"🔧 [DEBUG] Created new company from 'Other': {company.company_name}")
            
            return {
                "id": str(company.id),
                "company_name": company.company_name,
                "company_email": company.company_email,
                "contact_person": company.contact_person,
                "phone_number": company.phone_number,
                "additional_details": company.additional_details,
                "created_at": company.created_at.isoformat(),
                "updated_at": company.updated_at.isoformat() if company.updated_at else None,
                "is_active": company.is_active,
                "uploaded_by": company.uploaded_by
            }
            
    except Exception as e:
        print(f"🔧 [DEBUG] Error creating company from 'Other': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")


@router.post("/create-company", response_model=CompanyDetailsResponse)
async def create_company(
    company_name: str = Form(...),
    company_email: Optional[str] = Form(None),
    contact_person: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    additional_details: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a single company directly without CSV."""
    
    print(f"🔧 [DEBUG] Creating company: {company_name}")
    print(f"🔧 [DEBUG] Email: {company_email}, Contact: {contact_person}")
    
    if not company_name or not company_name.strip():
        raise HTTPException(status_code=400, detail="Company name is required")
    
    try:
        # Check if company already exists
        existing_company = db.query(CompanyDetails).filter(CompanyDetails.company_name == company_name.strip()).first()
        
        if existing_company:
            # Update existing company
            existing_company.company_email = company_email.strip() if company_email and company_email.strip() else None
            existing_company.contact_person = contact_person.strip() if contact_person and contact_person.strip() else None
            existing_company.phone_number = phone_number.strip() if phone_number and phone_number.strip() else None
            existing_company.additional_details = additional_details.strip() if additional_details and additional_details.strip() else None
            existing_company.updated_at = datetime.utcnow()
            
            db.commit()
            print(f"🔧 [DEBUG] Updated existing company: {existing_company.company_name}")
            
            return {
                "id": str(existing_company.id),
                "company_name": existing_company.company_name,
                "company_email": existing_company.company_email,
                "contact_person": existing_company.contact_person,
                "phone_number": existing_company.phone_number,
                "additional_details": existing_company.additional_details,
                "created_at": existing_company.created_at.isoformat(),
                "updated_at": existing_company.updated_at.isoformat() if existing_company.updated_at else None,
                "is_active": existing_company.is_active,
                "uploaded_by": existing_company.uploaded_by
            }
        else:
            # Create new company
            company = CompanyDetails(
                company_name=company_name.strip(),
                company_email=company_email.strip() if company_email and company_email.strip() else None,
                contact_person=contact_person.strip() if contact_person and contact_person.strip() else None,
                phone_number=phone_number.strip() if phone_number and phone_number.strip() else None,
                additional_details=additional_details.strip() if additional_details and additional_details.strip() else None,
                uploaded_by=current_user.id
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
            print(f"🔧 [DEBUG] Created new company: {company.company_name}")
            
            return {
                "id": str(company.id),
                "company_name": company.company_name,
                "company_email": company.company_email,
                "contact_person": company.contact_person,
                "phone_number": company.phone_number,
                "additional_details": company.additional_details,
                "created_at": company.created_at.isoformat(),
                "updated_at": company.updated_at.isoformat() if company.updated_at else None,
                "is_active": company.is_active,
                "uploaded_by": company.uploaded_by
            }
            
    except Exception as e:
        print(f"🔧 [DEBUG] Error creating company: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")


@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_companies_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload a CSV file containing company details."""
    
    print(f"🔧 [DEBUG] Received file: {file.filename}")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read and parse CSV file
        contents = await file.read()
        print(f"🔧 [DEBUG] File contents length: {len(contents)}")
        print(f"🔧 [DEBUG] File contents preview: {contents.decode('utf-8')[:200]}...")
        
        csv_reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))
        
        print(f"🔧 [DEBUG] CSV fieldnames: {csv_reader.fieldnames}")
        
        uploaded_companies = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 because header is row 1
            try:
                print(f"🔧 [DEBUG] Processing row {row_num}: {row}")
                
                # Validate required fields - only company_name is required
                company_name = row.get('company_name') or row.get('Company Name') or row.get('Company_Name')
                print(f"🔧 [DEBUG] Company name extracted: '{company_name}'")
                
                if not company_name or not company_name.strip():
                    errors.append(f"Row {row_num}: Missing required field (company_name)")
                    continue
                
                # Check if company already exists
                existing_company = db.query(CompanyDetails).filter(CompanyDetails.company_name == company_name.strip()).first()
                
                if existing_company:
                    # Update existing company
                    existing_company.company_email = (row.get('company_email') or row.get('Email') or '').strip() or None
                    existing_company.contact_person = (row.get('contact_person') or row.get('Contact Person') or row.get('Contact') or '').strip() or None
                    existing_company.phone_number = (row.get('phone_number') or row.get('Phone') or '').strip() or None
                    existing_company.additional_details = (row.get('additional_details') or row.get('Details') or '').strip() or None
                    existing_company.updated_at = datetime.utcnow()
                    uploaded_companies.append(existing_company)
                else:
                    # Create new company
                    company = CompanyDetails(
                        company_name=company_name.strip(),
                        company_email=(row.get('company_email') or row.get('Email') or '').strip() or None,
                        contact_person=(row.get('contact_person') or row.get('Contact Person') or row.get('Contact') or '').strip() or None,
                        phone_number=(row.get('phone_number') or row.get('Phone') or '').strip() or None,
                        additional_details=(row.get('additional_details') or row.get('Details') or '').strip() or None,
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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get list of uploaded companies with optional search and pagination."""
    
    query = db.query(CompanyDetails).order_by(CompanyDetails.created_at.desc())
    
    if search:
        query = query.filter(
            CompanyDetails.company_name.ilike(f"%{search}%")
        )
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    company_responses = [CompanyDetailsResponse.model_validate(company) for company in companies]
    
    return CompanyListResponse(
        companies=company_responses,
        total=total,
        failed=0,
        errors=[]
    )


@router.get("/public-companies")
@limiter.limit("10000/minute")  # Very high limit for public endpoint
async def get_public_companies(
    request: Request,
    search: Optional[str] = None,
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    # Check if companies module is enabled - read from env var directly for dynamic updates
    companies_enabled = os.environ.get("COMPANIES_MODULE_ENABLED", "true").lower() == "true"
    if not companies_enabled:
        return []  # Return empty list when module is disabled
    
    query = db.query(CompanyDetails).filter(CompanyDetails.is_active == True)
    
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




@router.put("/{company_id}", response_model=CompanyDetailsResponse)
async def update_company_details(
    company_id: int,
    company_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company details."""
    try:
        company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Update fields
        for field, value in company_update.items():
            if hasattr(company, field) and field not in ['id', 'uploaded_by', 'created_at']:
                setattr(company, field, value)
        
        company.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(company)
        
        return CompanyDetailsResponse.from_orm(company)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating company: {str(e)}")

@router.delete("/{company_id}")
async def delete_company_details(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete company details."""
    try:
        company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        db.delete(company)
        db.commit()
        
        return {"message": "Company deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting company: {str(e)}")


@router.get("/{company_id}", response_model=CompanyDetailsResponse)
async def get_company_details(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get specific company details by ID."""
    
    company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return CompanyDetailsResponse.from_orm(company)


@router.patch("/{company_id}/toggle-status")
async def toggle_company_status(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Enable or disable a company."""
    company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.is_active = not company.is_active
    db.commit()
    db.refresh(company)
    
    return {
        "message": f"Company {'enabled' if company.is_active else 'disabled'} successfully",
        "company": CompanyDetailsResponse.from_orm(company)
    }


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a company permanently."""
    print(f"🔧 [DEBUG] Backend: Delete request for company_id: {company_id}")
    print(f"🔧 [DEBUG] Backend: User making request: {current_user.email}")
    
    company = db.query(CompanyDetails).filter(CompanyDetails.id == company_id).first()
    
    if not company:
        print(f"🔧 [DEBUG] Backend: Company not found: {company_id}")
        raise HTTPException(status_code=404, detail="Company not found")
    
    print(f"🔧 [DEBUG] Backend: Found company to delete: {company.company_name}")
    
    db.delete(company)
    db.commit()
    
    print(f"🔧 [DEBUG] Backend: Company deleted successfully")
    
    return {"message": "Company deleted successfully"}


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
