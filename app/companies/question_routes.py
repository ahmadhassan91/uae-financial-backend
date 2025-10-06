"""API routes for company question set management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User, CompanyTracker, CustomerProfile
from ..auth.dependencies import get_current_admin_user, get_current_user
from .question_manager import CompanyQuestionManager
from .question_schemas import (
    QuestionSetCreate, QuestionSetUpdate, QuestionSetResponse,
    CompanyQuestionSetConfig, QuestionSetAnalytics, QuestionVariationCreate,
    QuestionVariationResponse, CompanyQuestionPreview, QuestionSetVersion,
    BulkQuestionSetOperation, BulkOperationResult
)

router = APIRouter(prefix="/companies", tags=["company-questions"])


@router.post("/{company_id}/question-sets", response_model=QuestionSetResponse)
async def create_question_set(
    company_id: int,
    question_set: QuestionSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new question set for a company. Admin only."""
    manager = CompanyQuestionManager(db)
    
    try:
        created_set = await manager.create_custom_question_set(
            company_id=company_id,
            name=question_set.name,
            description=question_set.description,
            base_questions=question_set.base_questions,
            custom_questions=question_set.custom_questions,
            excluded_questions=question_set.excluded_questions,
            question_variations=question_set.question_variations,
            demographic_rules=question_set.demographic_rules
        )
        return created_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{company_id}/question-sets", response_model=List[QuestionSetResponse])
async def list_question_sets(
    company_id: int,
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all question sets for a company. Admin only."""
    manager = CompanyQuestionManager(db)
    
    # Verify company exists
    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    versions = await manager.get_question_set_versions(company_id)
    
    if not include_inactive:
        versions = [v for v in versions if v.is_active]
    
    return versions


@router.get("/{company_id}/question-sets/{question_set_id}", response_model=QuestionSetResponse)
async def get_question_set(
    company_id: int,
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific question set. Admin only."""
    from ..models import CompanyQuestionSet
    
    question_set = db.query(CompanyQuestionSet).filter(
        CompanyQuestionSet.id == question_set_id,
        CompanyQuestionSet.company_tracker_id == company_id
    ).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    return question_set


@router.put("/{company_id}/question-sets/{question_set_id}", response_model=QuestionSetResponse)
async def update_question_set(
    company_id: int,
    question_set_id: int,
    updates: QuestionSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a question set (creates new version). Admin only."""
    manager = CompanyQuestionManager(db)
    
    try:
        updated_set = await manager.update_question_set(
            question_set_id, **updates.model_dump(exclude_unset=True)
        )
        return updated_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{company_id}/question-sets/{question_set_id}")
async def deactivate_question_set(
    company_id: int,
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deactivate a question set. Admin only."""
    from ..models import CompanyQuestionSet
    
    question_set = db.query(CompanyQuestionSet).filter(
        CompanyQuestionSet.id == question_set_id,
        CompanyQuestionSet.company_tracker_id == company_id
    ).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    question_set.is_active = False
    db.commit()
    
    return {"message": "Question set deactivated successfully"}


@router.post("/{company_id}/question-sets/{question_set_id}/rollback", response_model=QuestionSetResponse)
async def rollback_question_set(
    company_id: int,
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Rollback to a previous version of question set. Admin only."""
    manager = CompanyQuestionManager(db)
    
    try:
        rolled_back_set = await manager.rollback_to_version(company_id, question_set_id)
        return rolled_back_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{company_id}/question-sets/{question_set_id}/analytics", response_model=QuestionSetAnalytics)
async def get_question_set_analytics(
    company_id: int,
    question_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get analytics for a specific question set. Admin only."""
    manager = CompanyQuestionManager(db)
    
    analytics = await manager.get_question_set_analytics(company_id, question_set_id)
    return analytics


@router.post("/question-sets/preview", response_model=CompanyQuestionSetConfig)
async def preview_question_set(
    preview_request: CompanyQuestionPreview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview questions for a company URL with demographic profile."""
    manager = CompanyQuestionManager(db)
    
    # Convert demographic profile dict to CustomerProfile if provided
    demographic_profile = None
    if preview_request.demographic_profile:
        # Create a temporary profile object for preview
        demographic_profile = CustomerProfile(**preview_request.demographic_profile)
    
    question_set = await manager.get_company_question_set(
        company_url=preview_request.company_url,
        demographic_profile=demographic_profile,
        language=preview_request.language
    )
    
    return question_set


@router.get("/question-variations", response_model=List[QuestionVariationResponse])
async def list_question_variations(
    base_question_id: Optional[str] = Query(None),
    language: str = Query("en"),
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List available question variations. Admin only."""
    from ..models import QuestionVariation
    
    query = db.query(QuestionVariation).filter(QuestionVariation.is_active == True)
    
    if base_question_id:
        query = query.filter(QuestionVariation.base_question_id == base_question_id)
    
    if language:
        query = query.filter(QuestionVariation.language == language)
    
    if company_id:
        # Filter variations available for this company
        query = query.filter(
            (QuestionVariation.company_ids.is_(None)) |
            (QuestionVariation.company_ids.contains([company_id]))
        )
    
    variations = query.all()
    return variations


@router.post("/question-variations", response_model=QuestionVariationResponse)
async def create_question_variation(
    variation: QuestionVariationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new question variation. Admin only."""
    from ..models import QuestionVariation
    
    # Validate base question exists
    from ..surveys.question_definitions import SURVEY_QUESTIONS_V2
    valid_question_ids = {q.id for q in SURVEY_QUESTIONS_V2}
    
    if variation.base_question_id not in valid_question_ids:
        raise HTTPException(status_code=400, detail="Invalid base question ID")
    
    # Check if variation name already exists for this base question
    existing = db.query(QuestionVariation).filter(
        QuestionVariation.base_question_id == variation.base_question_id,
        QuestionVariation.variation_name == variation.variation_name,
        QuestionVariation.language == variation.language
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Variation with this name already exists for this question"
        )
    
    db_variation = QuestionVariation(**variation.model_dump())
    db.add(db_variation)
    db.commit()
    db.refresh(db_variation)
    
    return db_variation


@router.get("/{company_id}/question-sets/versions", response_model=List[QuestionSetVersion])
async def get_question_set_versions(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all versions of question sets for a company. Admin only."""
    manager = CompanyQuestionManager(db)
    
    versions = await manager.get_question_set_versions(company_id)
    
    # Convert to version info
    version_info = []
    for version in versions:
        total_questions = len(version.base_questions) + len(version.custom_questions or [])
        version_info.append(QuestionSetVersion(
            id=version.id,
            name=version.name,
            description=version.description,
            is_active=version.is_active,
            created_at=version.created_at,
            total_questions=total_questions
        ))
    
    return version_info


@router.post("/question-sets/bulk", response_model=BulkOperationResult)
async def bulk_question_set_operation(
    operation: BulkQuestionSetOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Perform bulk operations on question sets. Admin only."""
    from ..models import CompanyQuestionSet
    
    successful = 0
    failed = 0
    errors = []
    created_question_sets = []
    
    for company_id in operation.company_ids:
        try:
            if operation.operation == "activate":
                # Activate the most recent question set
                latest_set = db.query(CompanyQuestionSet).filter(
                    CompanyQuestionSet.company_tracker_id == company_id
                ).order_by(CompanyQuestionSet.created_at.desc()).first()
                
                if latest_set:
                    latest_set.is_active = True
                    db.commit()
                    successful += 1
                else:
                    failed += 1
                    errors.append({
                        "company_id": str(company_id),
                        "error": "No question sets found"
                    })
            
            elif operation.operation == "deactivate":
                # Deactivate all question sets for company
                db.query(CompanyQuestionSet).filter(
                    CompanyQuestionSet.company_tracker_id == company_id
                ).update({"is_active": False})
                db.commit()
                successful += 1
            
            elif operation.operation == "duplicate" and operation.source_question_set_id:
                # Duplicate question set from source
                source_set = db.query(CompanyQuestionSet).filter(
                    CompanyQuestionSet.id == operation.source_question_set_id
                ).first()
                
                if not source_set:
                    failed += 1
                    errors.append({
                        "company_id": str(company_id),
                        "error": "Source question set not found"
                    })
                    continue
                
                # Create new question set
                new_name = operation.new_name_template or f"{source_set.name} (Copy)"
                new_set = CompanyQuestionSet(
                    company_tracker_id=company_id,
                    name=new_name,
                    description=f"Duplicated from {source_set.name}",
                    base_questions=source_set.base_questions,
                    custom_questions=source_set.custom_questions,
                    excluded_questions=source_set.excluded_questions,
                    question_variations=source_set.question_variations,
                    demographic_rules=source_set.demographic_rules
                )
                
                db.add(new_set)
                db.commit()
                db.refresh(new_set)
                
                created_question_sets.append(new_set)
                successful += 1
            
            else:
                failed += 1
                errors.append({
                    "company_id": str(company_id),
                    "error": "Invalid operation or missing parameters"
                })
        
        except Exception as e:
            failed += 1
            errors.append({
                "company_id": str(company_id),
                "error": str(e)
            })
            db.rollback()
    
    return BulkOperationResult(
        successful=successful,
        failed=failed,
        errors=errors,
        created_question_sets=created_question_sets if created_question_sets else None
    )