"""Company management API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import string
from datetime import datetime, timedelta

from ..database import get_db
from ..models import CompanyTracker, CompanyAssessment, User
from ..auth.dependencies import get_current_user, get_current_admin_user, get_current_full_admin_user, get_current_full_admin_user
from ..config import settings
from .qr_utils import generate_qr_code, get_qr_code_metadata
from .schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyLinkConfig,
    CompanyLink, CompanyAnalytics, BulkCompanyCreate, BulkOperationResult
)
from typing import List

router = APIRouter(prefix="/companies", tags=["companies"])


def generate_unique_url(company_name: str, db: Session) -> str:
    """Generate a unique URL slug for a company."""
    # Clean company name to create a base slug
    base_slug = "".join(c.lower() for c in company_name if c.isalnum() or c.isspace()).replace(" ", "")
    
    # Try the base slug first
    if not db.query(CompanyTracker).filter(CompanyTracker.unique_url == base_slug).first():
        return base_slug
    
    # If base slug exists, try with incrementing numbers
    counter = 1
    while True:
        slug = f"{base_slug}{counter}"
        if not db.query(CompanyTracker).filter(CompanyTracker.unique_url == slug).first():
            return slug
        counter += 1


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new company for tracking. Admin only."""
    # Generate unique URL
    unique_url = generate_unique_url(company.company_name, db)
    
    # Create company tracker
    db_company = CompanyTracker(
        company_name=company.company_name,
        company_email=company.company_email,
        contact_person=company.contact_person,
        phone_number=company.phone_number,
        unique_url=unique_url,
        custom_branding=company.custom_branding,
        notification_settings=company.notification_settings,
        question_variation_mapping=company.question_variation_mapping,
        variation_set_id=company.variation_set_id
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company


@router.get("/export-csv")
async def export_companies_csv(
    include_analytics: bool = Query(False),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Export companies to CSV format. Admin only."""
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # Get companies
    query = db.query(CompanyTracker)
    if active_only:
        query = query.filter(CompanyTracker.is_active == True)
    
    companies = query.all()
    
    # Create CSV content
    output = io.StringIO()
    
    if include_analytics:
        fieldnames = [
            'id', 'company_name', 'company_email', 'contact_person', 'phone_number',
            'unique_url', 'total_assessments', 'average_score', 'is_active', 'created_at'
        ]
    else:
        fieldnames = [
            'company_name', 'company_email', 'contact_person', 'phone_number'
        ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for company in companies:
        if include_analytics:
            row = {
                'id': company.id,
                'company_name': company.company_name,
                'company_email': company.company_email,
                'contact_person': company.contact_person,
                'phone_number': company.phone_number or '',
                'unique_url': company.unique_url,
                'total_assessments': company.total_assessments,
                'average_score': company.average_score or '',
                'is_active': company.is_active,
                'created_at': company.created_at.isoformat()
            }
        else:
            row = {
                'company_name': company.company_name,
                'company_email': company.company_email,
                'contact_person': company.contact_person,
                'phone_number': company.phone_number or ''
            }
        
        writer.writerow(row)
    
    # Prepare response
    output.seek(0)
    
    filename = f"companies_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all companies. Admin only."""
    query = db.query(CompanyTracker)
    
    if active_only:
        query = query.filter(CompanyTracker.is_active == True)
    
    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific company by ID. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a company. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update fields
    for field, value in company_update.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a company and all related data. Admin only."""
    from app.models import CompanyAssessment, FinancialClinicResponse
    
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Delete all related data in correct order (children first, then parent)
    
    # 1. Delete financial clinic responses
    db.query(FinancialClinicResponse).filter(
        FinancialClinicResponse.company_tracker_id == company_id
    ).delete(synchronize_session=False)
    
    # 2. Delete company assessments
    db.query(CompanyAssessment).filter(
        CompanyAssessment.company_tracker_id == company_id
    ).delete(synchronize_session=False)
    
    # 3. Finally delete the company itself
    db.delete(company)
    db.commit()
    
    return {"message": "Company and all related data deleted successfully"}


@router.post("/{company_id}/generate-link", response_model=CompanyLink)
async def generate_company_link(
    company_id: int,
    config: Optional[CompanyLinkConfig] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Generate a magic link for a company. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Use existing unique_url or generate new one if config provided
    url_slug = company.unique_url
    if config and config.prefix and config.prefix != company.unique_url:
        # Check if new prefix is available
        existing_company = db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == config.prefix,
            CompanyTracker.id != company_id
        ).first()
        if existing_company:
            raise HTTPException(status_code=400, detail="URL prefix already in use")
        company.unique_url = config.prefix
        url_slug = config.prefix
        db.commit()
    
    # Generate full URL
    base_url = settings.base_url
    full_url = f"{base_url}/survey/c/{url_slug}"
    
    # Calculate expiry if specified
    expires_at = None
    if config and config.expiry_days is not None:
        if config.expiry_days == 0:
            # Create an immediately expired link for testing
            expires_at = datetime.utcnow() - timedelta(seconds=1)
        else:
            expires_at = datetime.utcnow() + timedelta(days=config.expiry_days)
    
    # Update company with link metadata
    if config:
        link_metadata = {
            "expires_at": expires_at.isoformat() if expires_at else None,
            "max_responses": config.max_responses,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user.id
        }
        company.notification_settings = company.notification_settings or {}
        company.notification_settings["current_link"] = link_metadata
        db.commit()
    
    # Generate QR code
    qr_code_data = generate_qr_code(
        url=full_url,
        company_id=company_id,
        company_name=company.company_name,
        expires_at=expires_at,
        size=(300, 300)
    )
    
    return CompanyLink(
        company_id=company_id,
        url=full_url,
        qr_code_url=qr_code_data,  # Base64 encoded QR code
        expires_at=expires_at,
        max_responses=config.max_responses if config else None
    )


@router.get("/{company_id}/analytics", response_model=CompanyAnalytics)
async def get_company_analytics(
    company_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    include_demographics: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive company analytics. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Build query for company assessments
    query = db.query(CompanyAssessment).filter(CompanyAssessment.company_tracker_id == company_id)
    
    if start_date:
        query = query.filter(CompanyAssessment.created_at >= start_date)
    if end_date:
        query = query.filter(CompanyAssessment.created_at <= end_date)
    
    assessments = query.all()
    total_responses = len(assessments)
    
    # Calculate score distribution
    at_risk = 0
    improvement_needed = 0
    good_health = 0
    excellent_health = 0
    total_score = 0
    
    # Demographics tracking
    age_distribution = {}
    gender_distribution = {}
    department_distribution = {}
    
    for assessment in assessments:
        score = assessment.overall_score
        total_score += score
        
        # Score categories
        if score < 30:
            at_risk += 1
        elif score < 45:
            improvement_needed += 1
        elif score < 60:
            good_health += 1
        else:
            excellent_health += 1
        
        # Demographics (if available in responses)
        if include_demographics and assessment.responses:
            responses = assessment.responses
            
            # Age distribution
            age = responses.get('age') or responses.get('age_range')
            if age:
                age_distribution[str(age)] = age_distribution.get(str(age), 0) + 1
            
            # Gender distribution
            gender = responses.get('gender')
            if gender:
                gender_distribution[str(gender)] = gender_distribution.get(str(gender), 0) + 1
            
            # Department distribution
            department = assessment.department
            if department:
                department_distribution[department] = department_distribution.get(department, 0) + 1
    
    # Calculate average score
    average_score = total_score / total_responses if total_responses > 0 else 0
    
    # Calculate participation rate (if we have employee count)
    participation_rate = None
    total_employees = None
    if company.custom_branding and company.custom_branding.get('total_employees'):
        total_employees = company.custom_branding['total_employees']
        participation_rate = (total_responses / total_employees) * 100 if total_employees > 0 else 0
    
    # Get industry and national averages (mock data for now)
    industry_average = 52.5  # This would come from industry benchmarks
    national_average = 48.3  # This would come from national statistics
    
    return CompanyAnalytics(
        company_id=company_id,
        company_name=company.company_name,
        total_employees=total_employees,
        total_responses=total_responses,
        participation_rate=participation_rate,
        average_score=average_score,
        industry_average=industry_average,
        national_average=national_average,
        age_distribution=age_distribution if age_distribution else None,
        gender_distribution=gender_distribution if gender_distribution else None,
        department_distribution=department_distribution if department_distribution else None,
        at_risk_employees=at_risk,
        improvement_needed=improvement_needed,
        good_health=good_health,
        excellent_health=excellent_health
    )


@router.post("/{company_id}/renew-link", response_model=CompanyLink)
async def renew_company_link(
    company_id: int,
    config: Optional[CompanyLinkConfig] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Renew an expired company link. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if current link exists and is expired
    current_link_info = None
    if company.notification_settings and "current_link" in company.notification_settings:
        current_link_info = company.notification_settings["current_link"]
        if current_link_info.get("expires_at"):
            expires_at_str = current_link_info["expires_at"]
            # Handle timezone parsing
            if expires_at_str.endswith('Z'):
                expires_at_str = expires_at_str[:-1] + '+00:00'
            elif '+' not in expires_at_str and 'T' in expires_at_str:
                expires_at_str = expires_at_str + '+00:00'
            
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at.tzinfo is not None:
                    expires_at = expires_at.replace(tzinfo=None)
                
                if expires_at > datetime.utcnow():
                    raise HTTPException(
                        status_code=400, 
                        detail="Current link is still valid. Use generate-link to create a new one."
                    )
            except ValueError:
                # If parsing fails, allow renewal
                pass
    
    # Use provided config or extend current settings
    if not config:
        config = CompanyLinkConfig(
            expiry_days=30,  # Default renewal period
            max_responses=current_link_info.get("max_responses", 1000) if current_link_info else 1000
        )
    
    # Generate renewed link (reuse same logic as generate_company_link)
    return await generate_company_link(company_id, config, db, current_user)


@router.get("/{company_id}/link-status")
async def get_link_status(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get current link status for a company. Admin only."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.notification_settings or "current_link" not in company.notification_settings:
        return {
            "company_id": company_id,
            "has_active_link": False,
            "url": f"{settings.base_url}/survey/c/{company.unique_url}",
            "message": "No link configuration found"
        }
    
    link_info = company.notification_settings["current_link"]
    expires_at = None
    is_expired = False
    
    if link_info.get("expires_at"):
        expires_at_str = link_info["expires_at"]
        # Handle both with and without timezone info
        if expires_at_str.endswith('Z'):
            expires_at_str = expires_at_str[:-1] + '+00:00'
        elif '+' not in expires_at_str and 'T' in expires_at_str:
            # Add UTC timezone if not present
            expires_at_str = expires_at_str + '+00:00'
        
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            # Convert to UTC for comparison
            if expires_at.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=None)
            is_expired = expires_at <= datetime.utcnow()
        except ValueError:
            # Fallback for parsing issues
            expires_at = datetime.fromisoformat(link_info["expires_at"])
            is_expired = expires_at <= datetime.utcnow()
    
    # Count current responses
    current_responses = db.query(CompanyAssessment).filter(
        CompanyAssessment.company_tracker_id == company_id
    ).count()
    
    max_responses = link_info.get("max_responses")
    is_over_limit = max_responses and current_responses >= max_responses
    
    return {
        "company_id": company_id,
        "url": f"{settings.base_url}/survey/c/{company.unique_url}",
        "has_active_link": not is_expired and not is_over_limit,
        "is_expired": is_expired,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "current_responses": current_responses,
        "max_responses": max_responses,
        "is_over_limit": is_over_limit,
        "generated_at": link_info.get("generated_at"),
        "generated_by": link_info.get("generated_by")
    }


@router.get("/analytics/comparison")
async def compare_companies(
    company_ids: str = Query(..., description="Comma-separated company IDs"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Compare analytics across multiple companies. Admin only."""
    
    # Parse company IDs
    try:
        ids = [int(id.strip()) for id in company_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid company IDs format")
    
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 companies can be compared at once")
    
    comparison_data = []
    
    for company_id in ids:
        company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
        if not company:
            continue
        
        # Get assessments for this company
        query = db.query(CompanyAssessment).filter(CompanyAssessment.company_tracker_id == company_id)
        
        if start_date:
            query = query.filter(CompanyAssessment.created_at >= start_date)
        if end_date:
            query = query.filter(CompanyAssessment.created_at <= end_date)
        
        assessments = query.all()
        total_responses = len(assessments)
        
        if total_responses == 0:
            avg_score = 0
            score_distribution = {"at_risk": 0, "improvement_needed": 0, "good_health": 0, "excellent_health": 0}
        else:
            total_score = sum(a.overall_score for a in assessments)
            avg_score = total_score / total_responses
            
            # Calculate distribution
            at_risk = sum(1 for a in assessments if a.overall_score < 30)
            improvement_needed = sum(1 for a in assessments if 30 <= a.overall_score < 45)
            good_health = sum(1 for a in assessments if 45 <= a.overall_score < 60)
            excellent_health = sum(1 for a in assessments if a.overall_score >= 60)
            
            score_distribution = {
                "at_risk": at_risk,
                "improvement_needed": improvement_needed,
                "good_health": good_health,
                "excellent_health": excellent_health
            }
        
        comparison_data.append({
            "company_id": company_id,
            "company_name": company.company_name,
            "total_responses": total_responses,
            "average_score": round(avg_score, 2),
            "score_distribution": score_distribution,
            "created_at": company.created_at.isoformat()
        })
    
    # Calculate benchmarks
    if comparison_data:
        all_scores = [c["average_score"] for c in comparison_data if c["average_score"] > 0]
        benchmark_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Add benchmark comparison
        for company in comparison_data:
            if company["average_score"] > 0:
                company["vs_benchmark"] = round(company["average_score"] - benchmark_score, 2)
            else:
                company["vs_benchmark"] = None
    
    return {
        "comparison_data": comparison_data,
        "benchmark_average": round(benchmark_score, 2) if comparison_data else 0,
        "total_companies": len(comparison_data),
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }


@router.get("/analytics/dashboard")
async def get_companies_dashboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("average_score", regex="^(company_name|total_responses|average_score|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get dashboard view of all companies with key metrics. Admin only."""
    
    # Get all companies with basic info
    companies_query = db.query(CompanyTracker).filter(CompanyTracker.is_active == True)
    
    # Apply sorting
    if sort_by == "company_name":
        companies_query = companies_query.order_by(
            CompanyTracker.company_name.asc() if sort_order == "asc" else CompanyTracker.company_name.desc()
        )
    elif sort_by == "total_responses":
        companies_query = companies_query.order_by(
            CompanyTracker.total_assessments.asc() if sort_order == "asc" else CompanyTracker.total_assessments.desc()
        )
    elif sort_by == "average_score":
        companies_query = companies_query.order_by(
            CompanyTracker.average_score.asc() if sort_order == "asc" else CompanyTracker.average_score.desc()
        )
    elif sort_by == "created_at":
        companies_query = companies_query.order_by(
            CompanyTracker.created_at.asc() if sort_order == "asc" else CompanyTracker.created_at.desc()
        )
    
    companies = companies_query.offset(skip).limit(limit).all()
    total_companies = db.query(CompanyTracker).filter(CompanyTracker.is_active == True).count()
    
    dashboard_data = []
    total_assessments = 0
    total_score_sum = 0
    companies_with_scores = 0
    
    for company in companies:
        # Get recent assessment count (last 30 days)
        recent_assessments = db.query(CompanyAssessment).filter(
            CompanyAssessment.company_tracker_id == company.id,
            CompanyAssessment.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Calculate health status
        health_status = "No Data"
        if company.average_score:
            if company.average_score >= 60:
                health_status = "Excellent"
            elif company.average_score >= 45:
                health_status = "Good"
            elif company.average_score >= 30:
                health_status = "Needs Improvement"
            else:
                health_status = "At Risk"
        
        dashboard_data.append({
            "id": company.id,
            "company_name": company.company_name,
            "contact_person": company.contact_person,
            "total_assessments": company.total_assessments,
            "recent_assessments": recent_assessments,
            "average_score": company.average_score,
            "health_status": health_status,
            "unique_url": company.unique_url,
            "created_at": company.created_at.isoformat(),
            "is_active": company.is_active
        })
        
        # Aggregate stats
        total_assessments += company.total_assessments
        if company.average_score:
            total_score_sum += company.average_score
            companies_with_scores += 1
    
    # Calculate overall statistics
    overall_average = total_score_sum / companies_with_scores if companies_with_scores > 0 else 0
    
    return {
        "companies": dashboard_data,
        "pagination": {
            "total": total_companies,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total_companies
        },
        "summary": {
            "total_companies": total_companies,
            "total_assessments": total_assessments,
            "overall_average_score": round(overall_average, 2),
            "companies_with_data": companies_with_scores
        },
        "sort": {
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    }


@router.post("/bulk", response_model=BulkOperationResult)
async def create_companies_bulk(
    bulk_data: BulkCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create multiple companies at once. Admin only."""
    successful = 0
    failed = 0
    errors = []
    generated_links = []
    created_companies = []
    
    for company_data in bulk_data.companies:
        try:
            # Generate unique URL
            unique_url = generate_unique_url(company_data.company_name, db)
            
            # Create company
            db_company = CompanyTracker(
                company_name=company_data.company_name,
                company_email=company_data.company_email,
                contact_person=company_data.contact_person,
                phone_number=company_data.phone_number,
                unique_url=unique_url,
                custom_branding=company_data.custom_branding,
                notification_settings=company_data.notification_settings
            )
            
            db.add(db_company)
            db.commit()
            db.refresh(db_company)
            
            created_companies.append(db_company)
            
            # Generate link if config provided
            if bulk_data.default_config:
                base_url = settings.base_url
                full_url = f"{base_url}/survey/c/{unique_url}"
                
                # Generate QR code if requested
                qr_code_data = None
                if bulk_data.default_config.custom_branding:
                    qr_code_data = generate_qr_code(
                        url=full_url,
                        company_id=db_company.id,
                        company_name=db_company.company_name,
                        size=(300, 300)
                    )
                
                generated_links.append(CompanyLink(
                    company_id=db_company.id,
                    url=full_url,
                    qr_code_url=qr_code_data,
                    expires_at=datetime.utcnow() + timedelta(days=bulk_data.default_config.expiry_days) if bulk_data.default_config.expiry_days else None,
                    max_responses=bulk_data.default_config.max_responses
                ))
            
            successful += 1
            
        except Exception as e:
            failed += 1
            errors.append({
                "company_name": company_data.company_name,
                "error": str(e)
            })
            db.rollback()
    
    return BulkOperationResult(
        successful=successful,
        failed=failed,
        errors=errors,
        generated_links=generated_links if generated_links else None
    )


@router.post("/import-csv")
async def import_companies_csv(
    file: UploadFile,
    generate_links: bool = Query(False),
    expiry_days: int = Query(30),
    max_responses: int = Query(1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Import companies from CSV file. Admin only."""
    import csv
    import io
    
    try:
        # Parse CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Expected columns: company_name, company_email, contact_person, phone_number
        required_columns = ['company_name', 'company_email', 'contact_person']
        
        # Validate CSV headers
        if not all(col in csv_reader.fieldnames for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        companies_data = []
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            if not row['company_name'].strip():
                continue  # Skip empty rows
            
            companies_data.append(CompanyCreate(
                company_name=row['company_name'].strip(),
                company_email=row['company_email'].strip(),
                contact_person=row['contact_person'].strip(),
                phone_number=row.get('phone_number', '').strip() or None
            ))
        
        if not companies_data:
            raise HTTPException(status_code=400, detail="No valid company data found in CSV")
        
        # Create bulk data object
        bulk_config = None
        if generate_links:
            bulk_config = CompanyLinkConfig(
                expiry_days=expiry_days,
                max_responses=max_responses,
                custom_branding=True
            )
        
        bulk_data = BulkCompanyCreate(
            companies=companies_data,
            default_config=bulk_config
        )
        
        # Use existing bulk creation logic
        result = await create_companies_bulk(bulk_data, db, current_user)
        
        return {
            "message": f"CSV import completed. {result.successful} companies created, {result.failed} failed.",
            "result": result
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid CSV file encoding. Please use UTF-8.")
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/bulk-generate-links")
async def bulk_generate_links(
    company_ids: List[int],
    config: CompanyLinkConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Generate links for multiple companies at once. Admin only."""
    
    if len(company_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 companies can be processed at once")
    
    successful = 0
    failed = 0
    errors = []
    generated_links = []
    
    for company_id in company_ids:
        try:
            company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
            if not company:
                errors.append({
                    "company_id": company_id,
                    "error": "Company not found"
                })
                failed += 1
                continue
            
            # Generate link using existing logic
            link_data = await generate_company_link(company_id, config, db, current_user)
            generated_links.append(link_data)
            successful += 1
            
        except Exception as e:
            failed += 1
            errors.append({
                "company_id": company_id,
                "error": str(e)
            })
    
    return {
        "successful": successful,
        "failed": failed,
        "errors": errors,
        "generated_links": generated_links
    }


@router.post("/bulk-update")
async def bulk_update_companies(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update multiple companies at once. Admin only."""
    
    updates = request_data.get('updates', [])
    
    if len(updates) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 companies can be updated at once")
    
    successful = 0
    failed = 0
    errors = []
    
    for update_data in updates:
        try:
            company_id = update_data.get('id')
            if not company_id:
                errors.append({
                    "error": "Missing company ID in update data"
                })
                failed += 1
                continue
            
            company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
            if not company:
                errors.append({
                    "company_id": company_id,
                    "error": "Company not found"
                })
                failed += 1
                continue
            
            # Update allowed fields
            allowed_fields = ['company_name', 'company_email', 'contact_person', 'phone_number', 'is_active']
            
            for field, value in update_data.items():
                if field in allowed_fields and hasattr(company, field):
                    setattr(company, field, value)
            
            db.commit()
            successful += 1
            
        except Exception as e:
            failed += 1
            errors.append({
                "company_id": update_data.get('id', 'unknown'),
                "error": str(e)
            })
            db.rollback()
    
    return {
        "successful": successful,
        "failed": failed,
        "errors": errors
    }


@router.post("/reports/generate")
async def generate_automated_report(
    report_type: str = Query(..., regex="^(summary|detailed|comparison)$"),
    company_ids: Optional[str] = Query(None, description="Comma-separated company IDs for specific companies"),
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    include_charts: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Generate automated reports for companies. Admin only."""
    
    # Parse company IDs if provided
    target_companies = None
    if company_ids:
        try:
            target_companies = [int(id.strip()) for id in company_ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid company IDs format")
    
    # Get companies based on selection
    if target_companies:
        companies = db.query(CompanyTracker).filter(
            CompanyTracker.id.in_(target_companies),
            CompanyTracker.is_active == True
        ).all()
    else:
        companies = db.query(CompanyTracker).filter(CompanyTracker.is_active == True).all()
    
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found for report generation")
    
    # Generate report based on type
    if report_type == "summary":
        report_data = await generate_summary_report(companies, db)
    elif report_type == "detailed":
        report_data = await generate_detailed_report(companies, db)
    elif report_type == "comparison":
        if len(companies) < 2:
            raise HTTPException(status_code=400, detail="Comparison report requires at least 2 companies")
        report_data = await generate_comparison_report(companies, db)
    
    # Add metadata
    report_data["metadata"] = {
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.email,
        "report_type": report_type,
        "companies_count": len(companies),
        "format": format
    }
    
    # Return based on format
    if format == "json":
        return report_data
    elif format == "csv":
        return await export_report_csv(report_data, report_type)
    elif format == "pdf":
        # PDF generation would require additional libraries like reportlab
        raise HTTPException(status_code=501, detail="PDF format not yet implemented")


async def generate_summary_report(companies: List[CompanyTracker], db: Session):
    """Generate a summary report for companies."""
    
    total_companies = len(companies)
    total_assessments = sum(c.total_assessments for c in companies)
    companies_with_data = sum(1 for c in companies if c.total_assessments > 0)
    
    # Calculate overall statistics
    total_score = sum(c.average_score * c.total_assessments for c in companies if c.average_score and c.total_assessments > 0)
    overall_average = total_score / total_assessments if total_assessments > 0 else 0
    
    # Health distribution across all companies
    health_distribution = {"excellent": 0, "good": 0, "needs_improvement": 0, "at_risk": 0}
    
    for company in companies:
        if company.average_score:
            if company.average_score >= 60:
                health_distribution["excellent"] += 1
            elif company.average_score >= 45:
                health_distribution["good"] += 1
            elif company.average_score >= 30:
                health_distribution["needs_improvement"] += 1
            else:
                health_distribution["at_risk"] += 1
    
    # Top performing companies
    top_companies = sorted(
        [c for c in companies if c.average_score],
        key=lambda x: x.average_score,
        reverse=True
    )[:5]
    
    return {
        "report_type": "summary",
        "overview": {
            "total_companies": total_companies,
            "companies_with_data": companies_with_data,
            "total_assessments": total_assessments,
            "overall_average_score": round(overall_average, 2)
        },
        "health_distribution": health_distribution,
        "top_performers": [
            {
                "company_name": c.company_name,
                "average_score": round(c.average_score, 2),
                "total_assessments": c.total_assessments
            }
            for c in top_companies
        ],
        "recommendations": generate_recommendations(companies)
    }


async def generate_detailed_report(companies: List[CompanyTracker], db: Session):
    """Generate a detailed report for companies."""
    
    detailed_data = []
    
    for company in companies:
        # Get assessments for detailed analysis
        assessments = db.query(CompanyAssessment).filter(
            CompanyAssessment.company_tracker_id == company.id
        ).all()
        
        # Calculate detailed metrics
        score_distribution = {"at_risk": 0, "improvement": 0, "good": 0, "excellent": 0}
        department_breakdown = {}
        
        for assessment in assessments:
            score = assessment.overall_score
            if score < 30:
                score_distribution["at_risk"] += 1
            elif score < 45:
                score_distribution["improvement"] += 1
            elif score < 60:
                score_distribution["good"] += 1
            else:
                score_distribution["excellent"] += 1
            
            # Department analysis
            if assessment.department:
                dept = assessment.department
                if dept not in department_breakdown:
                    department_breakdown[dept] = {"count": 0, "total_score": 0}
                department_breakdown[dept]["count"] += 1
                department_breakdown[dept]["total_score"] += score
        
        # Calculate department averages
        for dept in department_breakdown:
            dept_data = department_breakdown[dept]
            dept_data["average_score"] = dept_data["total_score"] / dept_data["count"]
        
        detailed_data.append({
            "company_id": company.id,
            "company_name": company.company_name,
            "contact_person": company.contact_person,
            "total_assessments": company.total_assessments,
            "average_score": company.average_score,
            "score_distribution": score_distribution,
            "department_breakdown": department_breakdown,
            "unique_url": company.unique_url,
            "created_at": company.created_at.isoformat()
        })
    
    return {
        "report_type": "detailed",
        "companies": detailed_data,
        "summary": {
            "total_companies": len(companies),
            "total_assessments": sum(c.total_assessments for c in companies)
        }
    }


async def generate_comparison_report(companies: List[CompanyTracker], db: Session):
    """Generate a comparison report for companies."""
    
    comparison_data = []
    
    for company in companies:
        assessments = db.query(CompanyAssessment).filter(
            CompanyAssessment.company_tracker_id == company.id
        ).all()
        
        # Calculate metrics for comparison
        participation_rate = None
        if company.custom_branding and company.custom_branding.get('total_employees'):
            total_employees = company.custom_branding['total_employees']
            participation_rate = (company.total_assessments / total_employees) * 100
        
        comparison_data.append({
            "company_name": company.company_name,
            "total_assessments": company.total_assessments,
            "average_score": company.average_score or 0,
            "participation_rate": participation_rate,
            "health_status": get_health_status(company.average_score),
            "created_at": company.created_at.isoformat()
        })
    
    # Sort by average score for ranking
    comparison_data.sort(key=lambda x: x["average_score"], reverse=True)
    
    # Add rankings
    for i, company_data in enumerate(comparison_data):
        company_data["rank"] = i + 1
    
    # Calculate benchmarks
    scores = [c["average_score"] for c in comparison_data if c["average_score"] > 0]
    benchmark_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "report_type": "comparison",
        "companies": comparison_data,
        "benchmark": {
            "average_score": round(benchmark_score, 2),
            "companies_compared": len(comparison_data),
            "companies_with_data": len(scores)
        }
    }


def get_health_status(average_score):
    """Get health status based on average score."""
    if not average_score:
        return "No Data"
    elif average_score >= 60:
        return "Excellent"
    elif average_score >= 45:
        return "Good"
    elif average_score >= 30:
        return "Needs Improvement"
    else:
        return "At Risk"


def generate_recommendations(companies: List[CompanyTracker]):
    """Generate recommendations based on company data."""
    recommendations = []
    
    companies_with_data = [c for c in companies if c.average_score and c.total_assessments > 0]
    
    if not companies_with_data:
        recommendations.append("Encourage companies to promote the financial health assessment to their employees.")
        return recommendations
    
    # Low participation companies
    low_participation = [c for c in companies_with_data if c.total_assessments < 10]
    if low_participation:
        recommendations.append(f"{len(low_participation)} companies have low participation. Consider targeted outreach campaigns.")
    
    # Low scoring companies
    low_scoring = [c for c in companies_with_data if c.average_score < 40]
    if low_scoring:
        recommendations.append(f"{len(low_scoring)} companies show concerning financial health scores. Prioritize financial wellness programs.")
    
    # High performing companies
    high_performing = [c for c in companies_with_data if c.average_score >= 60]
    if high_performing:
        recommendations.append(f"{len(high_performing)} companies demonstrate excellent financial health. Consider them for case studies.")
    
    return recommendations


async def export_report_csv(report_data: dict, report_type: str):
    """Export report data as CSV."""
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    
    if report_type == "summary":
        # Export top performers
        fieldnames = ['company_name', 'average_score', 'total_assessments']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for company in report_data.get('top_performers', []):
            writer.writerow(company)
    
    elif report_type == "detailed":
        # Export detailed company data
        fieldnames = ['company_name', 'contact_person', 'total_assessments', 'average_score', 'unique_url']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for company in report_data.get('companies', []):
            writer.writerow({
                'company_name': company['company_name'],
                'contact_person': company['contact_person'],
                'total_assessments': company['total_assessments'],
                'average_score': company['average_score'],
                'unique_url': company['unique_url']
            })
    
    elif report_type == "comparison":
        # Export comparison data
        fieldnames = ['rank', 'company_name', 'average_score', 'total_assessments', 'health_status']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for company in report_data.get('companies', []):
            writer.writerow({
                'rank': company['rank'],
                'company_name': company['company_name'],
                'average_score': company['average_score'],
                'total_assessments': company['total_assessments'],
                'health_status': company['health_status']
            })
    
    output.seek(0)
    
    filename = f"{report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/by-url/{company_url}")
async def get_company_by_url(
    company_url: str,
    db: Session = Depends(get_db)
):
    """
    Get company information by unique URL. Public endpoint (no auth required).
    Used for validating company links on the frontend.
    
    Returns:
        Basic company info: name, email, contact person, active status
    """
    company = db.query(CompanyTracker).filter(
        CompanyTracker.unique_url == company_url
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.is_active:
        raise HTTPException(status_code=403, detail="Company link is no longer active")
    
    # Return only public information
    return {
        "id": company.id,
        "company_name": company.company_name,
        "company_email": company.company_email,
        "contact_person": company.contact_person,
        "unique_url": company.unique_url,
        "is_active": company.is_active,
        "custom_branding": company.custom_branding
    }