"""
Admin API routes for managing Variation Sets.

This module provides CRUD endpoints for variation sets and company assignment functionality.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import VariationSet, QuestionVariation, CompanyTracker
from app.admin.schemas import (
    VariationSetCreate,
    VariationSetUpdate,
    VariationSetResponse,
    VariationSetListResponse,
    VariationSetCloneRequest,
    CompanySetAssignmentRequest,
    CompanySetAssignmentResponse
)
from app.auth import require_admin

router = APIRouter(prefix="/admin/variation-sets", tags=["Admin - Variation Sets"])


@router.post("", response_model=VariationSetResponse, status_code=201)
async def create_variation_set(
    variation_set: VariationSetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new variation set with all 15 question variations.
    
    - Validates all question variation IDs exist
    - Creates a complete set ready for company assignment
    """
    # Validate all question variation IDs exist
    variation_ids = [
        variation_set.q1_variation_id, variation_set.q2_variation_id,
        variation_set.q3_variation_id, variation_set.q4_variation_id,
        variation_set.q5_variation_id, variation_set.q6_variation_id,
        variation_set.q7_variation_id, variation_set.q8_variation_id,
        variation_set.q9_variation_id, variation_set.q10_variation_id,
        variation_set.q11_variation_id, variation_set.q12_variation_id,
        variation_set.q13_variation_id, variation_set.q14_variation_id,
        variation_set.q15_variation_id
    ]
    
    # Check all variations exist
    existing_variations = db.query(QuestionVariation.id).filter(
        QuestionVariation.id.in_(variation_ids)
    ).all()
    existing_ids = {v.id for v in existing_variations}
    
    missing_ids = set(variation_ids) - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Question variation IDs not found: {sorted(missing_ids)}"
        )
    
    # Check for duplicate name
    existing_set = db.query(VariationSet).filter(
        VariationSet.name == variation_set.name
    ).first()
    if existing_set:
        raise HTTPException(
            status_code=400,
            detail=f"Variation set with name '{variation_set.name}' already exists"
        )
    
    # Create the variation set
    db_variation_set = VariationSet(**variation_set.model_dump())
    db.add(db_variation_set)
    db.commit()
    db.refresh(db_variation_set)
    
    return db_variation_set


@router.get("", response_model=VariationSetListResponse)
async def list_variation_sets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    set_type: Optional[str] = Query(None, description="Filter by set type"),
    is_template: Optional[bool] = Query(None, description="Filter templates"),
    is_active: Optional[bool] = Query(None, description="Filter active sets"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    List all variation sets with pagination and filtering.
    
    - Supports filtering by type, template status, active status
    - Includes company usage count
    """
    query = db.query(VariationSet)
    
    # Apply filters
    if set_type:
        query = query.filter(VariationSet.set_type == set_type)
    if is_template is not None:
        query = query.filter(VariationSet.is_template == is_template)
    if is_active is not None:
        query = query.filter(VariationSet.is_active == is_active)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (VariationSet.name.ilike(search_filter)) |
            (VariationSet.description.ilike(search_filter))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    variation_sets = query.order_by(VariationSet.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Add company usage count to each set
    response_sets = []
    for vs in variation_sets:
        vs_dict = {
            "id": vs.id,
            "name": vs.name,
            "description": vs.description,
            "set_type": vs.set_type,
            "is_template": vs.is_template,
            "is_active": vs.is_active,
            "created_at": vs.created_at,
            "updated_at": vs.updated_at,
            "q1_variation_id": vs.q1_variation_id,
            "q2_variation_id": vs.q2_variation_id,
            "q3_variation_id": vs.q3_variation_id,
            "q4_variation_id": vs.q4_variation_id,
            "q5_variation_id": vs.q5_variation_id,
            "q6_variation_id": vs.q6_variation_id,
            "q7_variation_id": vs.q7_variation_id,
            "q8_variation_id": vs.q8_variation_id,
            "q9_variation_id": vs.q9_variation_id,
            "q10_variation_id": vs.q10_variation_id,
            "q11_variation_id": vs.q11_variation_id,
            "q12_variation_id": vs.q12_variation_id,
            "q13_variation_id": vs.q13_variation_id,
            "q14_variation_id": vs.q14_variation_id,
            "q15_variation_id": vs.q15_variation_id,
            "companies_using_count": db.query(func.count(CompanyTracker.id)).filter(
                CompanyTracker.variation_set_id == vs.id
            ).scalar()
        }
        response_sets.append(VariationSetResponse(**vs_dict))
    
    return {
        "variation_sets": response_sets,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{set_id}", response_model=VariationSetResponse)
async def get_variation_set(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Get a specific variation set by ID with company usage count."""
    variation_set = db.query(VariationSet).filter(VariationSet.id == set_id).first()
    if not variation_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    # Add company usage count
    companies_using_count = db.query(func.count(CompanyTracker.id)).filter(
        CompanyTracker.variation_set_id == set_id
    ).scalar()
    
    response_dict = {
        "id": variation_set.id,
        "name": variation_set.name,
        "description": variation_set.description,
        "set_type": variation_set.set_type,
        "is_template": variation_set.is_template,
        "is_active": variation_set.is_active,
        "created_at": variation_set.created_at,
        "updated_at": variation_set.updated_at,
        "q1_variation_id": variation_set.q1_variation_id,
        "q2_variation_id": variation_set.q2_variation_id,
        "q3_variation_id": variation_set.q3_variation_id,
        "q4_variation_id": variation_set.q4_variation_id,
        "q5_variation_id": variation_set.q5_variation_id,
        "q6_variation_id": variation_set.q6_variation_id,
        "q7_variation_id": variation_set.q7_variation_id,
        "q8_variation_id": variation_set.q8_variation_id,
        "q9_variation_id": variation_set.q9_variation_id,
        "q10_variation_id": variation_set.q10_variation_id,
        "q11_variation_id": variation_set.q11_variation_id,
        "q12_variation_id": variation_set.q12_variation_id,
        "q13_variation_id": variation_set.q13_variation_id,
        "q14_variation_id": variation_set.q14_variation_id,
        "q15_variation_id": variation_set.q15_variation_id,
        "companies_using_count": companies_using_count
    }
    
    return VariationSetResponse(**response_dict)


@router.put("/{set_id}", response_model=VariationSetResponse)
async def update_variation_set(
    set_id: int,
    variation_set_update: VariationSetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update an existing variation set."""
    db_variation_set = db.query(VariationSet).filter(VariationSet.id == set_id).first()
    if not db_variation_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    # Validate question variation IDs if provided
    variation_ids = []
    update_data = variation_set_update.model_dump(exclude_unset=True)
    
    for i in range(1, 16):
        field_name = f"q{i}_variation_id"
        if field_name in update_data:
            variation_ids.append(update_data[field_name])
    
    if variation_ids:
        existing_variations = db.query(QuestionVariation.id).filter(
            QuestionVariation.id.in_(variation_ids)
        ).all()
        existing_ids = {v.id for v in existing_variations}
        
        missing_ids = set(variation_ids) - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Question variation IDs not found: {sorted(missing_ids)}"
            )
    
    # Check for duplicate name if name is being updated
    if "name" in update_data and update_data["name"] != db_variation_set.name:
        existing_set = db.query(VariationSet).filter(
            VariationSet.name == update_data["name"],
            VariationSet.id != set_id
        ).first()
        if existing_set:
            raise HTTPException(
                status_code=400,
                detail=f"Variation set with name '{update_data['name']}' already exists"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_variation_set, field, value)
    
    db.commit()
    db.refresh(db_variation_set)
    
    return db_variation_set


@router.delete("/{set_id}", status_code=204)
async def delete_variation_set(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a variation set.
    
    - Prevents deletion if any companies are using this set
    """
    db_variation_set = db.query(VariationSet).filter(VariationSet.id == set_id).first()
    if not db_variation_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    # Check if any companies are using this set
    companies_using = db.query(func.count(CompanyTracker.id)).filter(
        CompanyTracker.variation_set_id == set_id
    ).scalar()
    
    if companies_using > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete variation set: {companies_using} companies are using it"
        )
    
    db.delete(db_variation_set)
    db.commit()
    
    return None


@router.post("/{set_id}/clone", response_model=VariationSetResponse, status_code=201)
async def clone_variation_set(
    set_id: int,
    clone_request: VariationSetCloneRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Clone an existing variation set.
    
    - Creates a copy with a new name
    - Cloned sets are not templates by default
    """
    original_set = db.query(VariationSet).filter(VariationSet.id == set_id).first()
    if not original_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    # Check for duplicate name
    existing_set = db.query(VariationSet).filter(
        VariationSet.name == clone_request.new_name
    ).first()
    if existing_set:
        raise HTTPException(
            status_code=400,
            detail=f"Variation set with name '{clone_request.new_name}' already exists"
        )
    
    # Create new set
    new_set = VariationSet(
        name=clone_request.new_name,
        description=clone_request.new_description or original_set.description,
        set_type=original_set.set_type,
        is_template=False,  # Cloned sets are not templates
        is_active=original_set.is_active,
        q1_variation_id=original_set.q1_variation_id,
        q2_variation_id=original_set.q2_variation_id,
        q3_variation_id=original_set.q3_variation_id,
        q4_variation_id=original_set.q4_variation_id,
        q5_variation_id=original_set.q5_variation_id,
        q6_variation_id=original_set.q6_variation_id,
        q7_variation_id=original_set.q7_variation_id,
        q8_variation_id=original_set.q8_variation_id,
        q9_variation_id=original_set.q9_variation_id,
        q10_variation_id=original_set.q10_variation_id,
        q11_variation_id=original_set.q11_variation_id,
        q12_variation_id=original_set.q12_variation_id,
        q13_variation_id=original_set.q13_variation_id,
        q14_variation_id=original_set.q14_variation_id,
        q15_variation_id=original_set.q15_variation_id,
    )
    
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    
    return new_set


@router.put("/companies/{company_id}/assign-set", response_model=CompanySetAssignmentResponse)
async def assign_set_to_company(
    company_id: int,
    assignment: CompanySetAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Assign a variation set to a company.
    
    - Replaces any existing set assignment
    - Validates the variation set exists and is active
    """
    # Check company exists
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check variation set exists and is active
    variation_set = db.query(VariationSet).filter(
        VariationSet.id == assignment.variation_set_id
    ).first()
    if not variation_set:
        raise HTTPException(status_code=404, detail="Variation set not found")
    
    if not variation_set.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign an inactive variation set"
        )
    
    # Assign the set
    company.variation_set_id = assignment.variation_set_id
    db.commit()
    db.refresh(company)
    
    return {
        "company_id": company.id,
        "company_name": company.company_name,
        "variation_set_id": variation_set.id,
        "variation_set_name": variation_set.name,
        "updated_at": company.updated_at
    }


@router.delete("/companies/{company_id}/assign-set", status_code=204)
async def unassign_set_from_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Remove variation set assignment from a company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.variation_set_id = None
    db.commit()
    
    return None


@router.get("/companies/{company_id}/assigned-set", response_model=CompanySetAssignmentResponse)
async def get_company_assigned_set(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Get the variation set assigned to a company."""
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    variation_set_name = None
    if company.variation_set_id:
        variation_set = db.query(VariationSet).filter(
            VariationSet.id == company.variation_set_id
        ).first()
        if variation_set:
            variation_set_name = variation_set.name
    
    return {
        "company_id": company.id,
        "company_name": company.company_name,
        "variation_set_id": company.variation_set_id,
        "variation_set_name": variation_set_name,
        "updated_at": company.updated_at
    }
