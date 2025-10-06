"""API routes for URL-based configuration management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, CustomerProfile
from ..auth.dependencies import get_current_admin_user, get_current_user
from .url_config_service import URLConfigurationService

router = APIRouter(prefix="/config", tags=["url-configuration"])


@router.get("/url/{company_url}")
async def get_url_configuration(
    company_url: str,
    language: str = Query("en"),
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get configuration for a company URL."""
    
    config_service = URLConfigurationService(db)
    
    try:
        config = await config_service.get_configuration_for_url(
            company_url=company_url,
            language=language,
            force_refresh=force_refresh
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/url/{company_url}/with-profile")
async def get_url_configuration_with_profile(
    company_url: str,
    nationality: str = Query(...),
    age: int = Query(...),
    emirate: str = Query(...),
    employment_status: str = Query(...),
    monthly_income: str = Query(...),
    language: str = Query("en"),
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get configuration for a company URL with demographic profile."""
    
    # Create temporary profile for configuration
    temp_profile = CustomerProfile(
        nationality=nationality,
        age=age,
        emirate=emirate,
        employment_status=employment_status,
        monthly_income=monthly_income,
        first_name="temp",
        last_name="temp",
        gender="temp",
        household_size=1
    )
    
    config_service = URLConfigurationService(db)
    
    try:
        config = await config_service.get_configuration_for_url(
            company_url=company_url,
            demographic_profile=temp_profile,
            language=language,
            force_refresh=force_refresh
        )
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/url/{company_url}/mapping")
async def get_url_mapping(
    company_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get URL to configuration mapping. Admin only."""
    
    config_service = URLConfigurationService(db)
    
    mapping = await config_service.get_url_mapping(company_url)
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Company URL not found")
    
    return mapping


@router.post("/url/{company_url}/validate")
async def validate_configuration(
    company_url: str,
    config_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Validate a configuration before applying it. Admin only."""
    
    config_service = URLConfigurationService(db)
    
    validation_result = await config_service.validate_configuration(
        company_url, config_data
    )
    
    return validation_result


@router.get("/url/{company_url}/hierarchy")
async def get_configuration_hierarchy(
    company_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get the configuration hierarchy for a company. Admin only."""
    
    config_service = URLConfigurationService(db)
    
    hierarchy = await config_service.get_configuration_hierarchy(company_url)
    
    return hierarchy


@router.post("/url/{company_url}/cache/invalidate")
async def invalidate_url_cache(
    company_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Invalidate cache for a company URL. Admin only."""
    
    from ..models import CompanyTracker
    
    # Get company ID from URL
    company = db.query(CompanyTracker).filter(
        CompanyTracker.unique_url == company_url
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    config_service = URLConfigurationService(db)
    
    await config_service.invalidate_cache_for_company(company.id)
    
    return {"message": f"Cache invalidated for company URL: {company_url}"}


@router.post("/cache/invalidate-all")
async def invalidate_all_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Invalidate all URL configuration cache. Admin only."""
    
    from ..models import CompanyTracker
    
    config_service = URLConfigurationService(db)
    
    # Get all companies
    companies = db.query(CompanyTracker).filter(
        CompanyTracker.is_active == True
    ).all()
    
    invalidated_count = 0
    for company in companies:
        try:
            await config_service.invalidate_cache_for_company(company.id)
            invalidated_count += 1
        except Exception as e:
            # Log error but continue
            pass
    
    return {
        "message": f"Cache invalidated for {invalidated_count} companies",
        "total_companies": len(companies)
    }


@router.get("/url/{company_url}/preview")
async def preview_configuration(
    company_url: str,
    language: str = Query("en"),
    nationality: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    emirate: Optional[str] = Query(None),
    employment_status: Optional[str] = Query(None),
    monthly_income: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview configuration for a company URL with optional demographic filters."""
    
    demographic_profile = None
    if all([nationality, age, emirate, employment_status, monthly_income]):
        demographic_profile = CustomerProfile(
            nationality=nationality,
            age=age,
            emirate=emirate,
            employment_status=employment_status,
            monthly_income=monthly_income,
            first_name="preview",
            last_name="preview",
            gender="preview",
            household_size=1
        )
    
    config_service = URLConfigurationService(db)
    
    config = await config_service.get_configuration_for_url(
        company_url=company_url,
        demographic_profile=demographic_profile,
        language=language,
        force_refresh=True  # Always get fresh data for preview
    )
    
    # Add preview metadata
    config["preview_mode"] = True
    config["preview_timestamp"] = datetime.utcnow().isoformat()
    
    return config


@router.get("/defaults")
async def get_default_configuration(
    current_user: User = Depends(get_current_admin_user)
):
    """Get the default system configuration. Admin only."""
    
    config_service = URLConfigurationService(None)  # No DB needed for defaults
    
    return config_service._get_default_configuration()


@router.post("/url/{company_url}/inheritance")
async def apply_configuration_inheritance(
    company_url: str,
    company_config: Dict[str, Any],
    parent_config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Apply configuration inheritance and return the final config. Admin only."""
    
    config_service = URLConfigurationService(db)
    
    final_config = await config_service.apply_configuration_inheritance(
        company_config, parent_config
    )
    
    return {
        "company_url": company_url,
        "final_config": final_config,
        "inheritance_applied": True
    }