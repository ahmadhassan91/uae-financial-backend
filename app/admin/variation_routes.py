"""
Admin routes for managing question variations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User, CompanyTracker, VariationSet, QuestionVariation

router = APIRouter(prefix="/admin/variations", tags=["admin-variations"])

class VariationStatusResponse(BaseModel):
    company_id: int
    company_name: str
    unique_url: str
    enable_variations: bool
    variation_set_id: Optional[int]
    variation_set_name: Optional[str]
    variations_enabled_at: Optional[str]
    variations_enabled_by: Optional[str]

class ToggleVariationsRequest(BaseModel):
    enable_variations: bool
    reason: Optional[str] = None

@router.get("/companies/{company_id}/status", response_model=VariationStatusResponse)
async def get_variation_status(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get variation status for a specific company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    variation_set_name = None
    if company.variation_set_id:
        variation_set = db.query(VariationSet).filter(VariationSet.id == company.variation_set_id).first()
        variation_set_name = variation_set.name if variation_set else None
    
    enabled_by_name = None
    if company.variations_enabled_by:
        enabled_by_user = db.query(User).filter(User.id == company.variations_enabled_by).first()
        enabled_by_name = enabled_by_user.username if enabled_by_user else None
    
    return VariationStatusResponse(
        company_id=company.id,
        company_name=getattr(company, 'name', f'Company {company.id}'),
        unique_url=company.unique_url,
        enable_variations=company.enable_variations,
        variation_set_id=company.variation_set_id,
        variation_set_name=variation_set_name,
        variations_enabled_at=company.variations_enabled_at.isoformat() if company.variations_enabled_at else None,
        variations_enabled_by=enabled_by_name
    )

@router.post("/companies/{company_id}/toggle")
async def toggle_variations(
    company_id: int,
    request: ToggleVariationsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Enable or disable variations for a company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update variation settings
    company.enable_variations = request.enable_variations
    
    if request.enable_variations:
        # Enabling variations
        if not company.variations_enabled_at:
            from datetime import datetime, timezone
            company.variations_enabled_at = datetime.now(timezone.utc)
            company.variations_enabled_by = current_user.id
        
        # Check if company has variation set
        if not company.variation_set_id and not company.question_variation_mapping:
            raise HTTPException(
                status_code=400, 
                detail="No variation set or mapping assigned to this company. Please assign variations first."
            )
    else:
        # Disabling variations - clear the enabled timestamp
        company.variations_enabled_at = None
        company.variations_enabled_by = None
    
    db.commit()
    
    action = "enabled" if request.enable_variations else "disabled"
    return {
        "message": f"Variations {action} for company {company.id}",
        "company_id": company.id,
        "enable_variations": company.enable_variations
    }

@router.get("/sets", response_model=List[dict])
async def get_variation_sets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all available variation sets."""
    sets = db.query(VariationSet).filter(VariationSet.is_active == True).all()
    return [
        {
            "id": variation_set.id,
            "name": variation_set.name,
            "description": variation_set.description,
            "set_type": variation_set.set_type,
            "is_template": variation_set.is_template
        }
        for variation_set in sets
    ]

@router.post("/companies/{company_id}/assign-set/{variation_set_id}")
async def assign_variation_set(
    company_id: int,
    variation_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Assign a variation set to a company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    variation_set = db.query(VariationSet).filter(VariationSet.id == variation_set_id).first()
    if not variation_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    # Assign the variation set
    company.variation_set_id = variation_set_id
    db.commit()
    
    return {
        "message": f"Variation set '{variation_set.name}' assigned to company {company.id}",
        "company_id": company.id,
        "variation_set_id": variation_set.id,
        "variation_set_name": variation_set.name
    }

@router.delete("/companies/{company_id}/unassign-variation-set")
async def unassign_variation_set(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Unassign variation set from a company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Clear the variation set and disable variations
    company.variation_set_id = None
    company.enable_variations = False
    company.variations_enabled_at = None
    company.variations_enabled_by = None
    db.commit()
    
    return {
        "message": f"Variation set unassigned from company {company.id}",
        "company_id": company.id
    }
