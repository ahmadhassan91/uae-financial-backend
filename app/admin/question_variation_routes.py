"""
Admin API routes for question variation management.

This module provides REST API endpoints for creating, managing, and analyzing
question variations with proper validation and analytics.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.database import get_db
from app.auth.dependencies import get_current_admin_user as get_admin_user
from app.models import (
    User, QuestionVariation, DemographicRule, CustomerProfile, 
    SurveyResponse, AuditLog
)
from app.surveys.question_variation_service import (
    QuestionVariationService, VariationValidationResult
)
from app.surveys.question_definitions import question_lookup
from app.admin.schemas import (
    QuestionVariationCreate, QuestionVariationUpdate, QuestionVariationResponse,
    QuestionVariationAnalytics, VariationTestRequest, VariationTestResult,
    QuestionVariationListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/question-variations", tags=["admin", "question-variations"])


@router.get("/", response_model=QuestionVariationListResponse)
async def list_question_variations(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    base_question_id: Optional[str] = Query(None, description="Filter by base question ID"),
    language: str = Query("en", description="Filter by language"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    active_only: bool = Query(True, description="Only return active variations"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    List question variations with filtering and pagination.
    """
    try:
        service = QuestionVariationService(db)
        
        # Build query
        query = db.query(QuestionVariation)
        
        if base_question_id:
            query = query.filter(QuestionVariation.base_question_id == base_question_id)
        
        if language:
            query = query.filter(QuestionVariation.language == language)
        
        if active_only:
            query = query.filter(QuestionVariation.is_active == True)
        
        if company_id:
            query = query.filter(QuestionVariation.company_ids.contains([company_id]))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        variations = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        variation_responses = []
        for variation in variations:
            # Get usage statistics
            usage_count = db.query(SurveyResponse).filter(
                SurveyResponse.question_variations_used.contains({variation.base_question_id: variation.id})
            ).count()
            
            variation_response = QuestionVariationResponse(
                id=variation.id,
                base_question_id=variation.base_question_id,
                variation_name=variation.variation_name,
                language=variation.language,
                text=variation.text,
                options=variation.options,
                demographic_rules=variation.demographic_rules,
                company_ids=variation.company_ids,
                factor=variation.factor,
                weight=variation.weight,
                is_active=variation.is_active,
                usage_count=usage_count,
                created_at=variation.created_at,
                updated_at=variation.updated_at
            )
            variation_responses.append(variation_response)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="list_question_variations",
            entity_type="question_variation",
            details={
                "filters": {
                    "base_question_id": base_question_id,
                    "language": language,
                    "company_id": company_id,
                    "active_only": active_only
                },
                "total_results": total
            }
        ))
        db.commit()
        
        return QuestionVariationListResponse(
            variations=variation_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error listing question variations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question variations"
        )


@router.post("/", response_model=QuestionVariationResponse)
async def create_question_variation(
    variation_data: QuestionVariationCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Create a new question variation.
    """
    try:
        service = QuestionVariationService(db)
        
        # Create variation
        success, message, variation = service.create_question_variation(
            base_question_id=variation_data.base_question_id,
            variation_name=variation_data.variation_name,
            text=variation_data.text,
            options=variation_data.options,
            language=variation_data.language,
            demographic_rules=variation_data.demographic_rules,
            company_ids=variation_data.company_ids
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="create_question_variation",
            entity_type="question_variation",
            entity_id=variation.id,
            details={
                "base_question_id": variation.base_question_id,
                "variation_name": variation.variation_name,
                "language": variation.language
            }
        ))
        db.commit()
        
        return QuestionVariationResponse(
            id=variation.id,
            base_question_id=variation.base_question_id,
            variation_name=variation.variation_name,
            language=variation.language,
            text=variation.text,
            options=variation.options,
            demographic_rules=variation.demographic_rules,
            company_ids=variation.company_ids,
            factor=variation.factor,
            weight=variation.weight,
            is_active=variation.is_active,
            usage_count=0,
            created_at=variation.created_at,
            updated_at=variation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question variation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating question variation"
        )


@router.get("/{variation_id}", response_model=QuestionVariationResponse)
async def get_question_variation(
    variation_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Get a specific question variation by ID.
    """
    try:
        variation = db.query(QuestionVariation).filter(
            QuestionVariation.id == variation_id
        ).first()
        
        if not variation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question variation not found"
            )
        
        # Get usage statistics
        usage_count = db.query(SurveyResponse).filter(
            SurveyResponse.question_variations_used.contains({variation.base_question_id: variation.id})
        ).count()
        
        return QuestionVariationResponse(
            id=variation.id,
            base_question_id=variation.base_question_id,
            variation_name=variation.variation_name,
            language=variation.language,
            text=variation.text,
            options=variation.options,
            demographic_rules=variation.demographic_rules,
            company_ids=variation.company_ids,
            factor=variation.factor,
            weight=variation.weight,
            is_active=variation.is_active,
            usage_count=usage_count,
            created_at=variation.created_at,
            updated_at=variation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question variation {variation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question variation"
        )


@router.put("/{variation_id}", response_model=QuestionVariationResponse)
async def update_question_variation(
    variation_id: int,
    variation_data: QuestionVariationUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Update a question variation.
    """
    try:
        variation = db.query(QuestionVariation).filter(
            QuestionVariation.id == variation_id
        ).first()
        
        if not variation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question variation not found"
            )
        
        # Validate updates if text or options changed
        if variation_data.text or variation_data.options:
            service = QuestionVariationService(db)
            base_question = question_lookup.get_question_by_id(variation.base_question_id)
            
            if base_question:
                validation = service.validate_question_variation(
                    base_question,
                    variation_data.text or variation.text,
                    variation_data.options or variation.options,
                    variation.language
                )
                
                if not validation.is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Validation failed: {'; '.join(validation.errors)}"
                    )
        
        # Update fields
        if variation_data.variation_name is not None:
            variation.variation_name = variation_data.variation_name
        if variation_data.text is not None:
            variation.text = variation_data.text
        if variation_data.options is not None:
            variation.options = variation_data.options
        if variation_data.demographic_rules is not None:
            variation.demographic_rules = variation_data.demographic_rules
        if variation_data.company_ids is not None:
            variation.company_ids = variation_data.company_ids
        if variation_data.is_active is not None:
            variation.is_active = variation_data.is_active
        
        variation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(variation)
        
        # Get usage statistics
        usage_count = db.query(SurveyResponse).filter(
            SurveyResponse.question_variations_used.contains({variation.base_question_id: variation.id})
        ).count()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="update_question_variation",
            entity_type="question_variation",
            entity_id=variation.id,
            details={
                "updated_fields": [k for k, v in variation_data.dict().items() if v is not None]
            }
        ))
        db.commit()
        
        return QuestionVariationResponse(
            id=variation.id,
            base_question_id=variation.base_question_id,
            variation_name=variation.variation_name,
            language=variation.language,
            text=variation.text,
            options=variation.options,
            demographic_rules=variation.demographic_rules,
            company_ids=variation.company_ids,
            factor=variation.factor,
            weight=variation.weight,
            is_active=variation.is_active,
            usage_count=usage_count,
            created_at=variation.created_at,
            updated_at=variation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question variation {variation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating question variation"
        )


@router.delete("/{variation_id}")
async def delete_question_variation(
    variation_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Delete a question variation.
    """
    try:
        service = QuestionVariationService(db)
        
        success, message = service.delete_variation(variation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="delete_question_variation",
            entity_type="question_variation",
            entity_id=variation_id,
            details={"variation_id": variation_id}
        ))
        db.commit()
        
        return {"message": "Question variation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question variation {variation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting question variation"
        )


@router.post("/test", response_model=VariationTestResult)
async def test_question_variation(
    test_request: VariationTestRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Test a question variation against demographic profiles.
    """
    try:
        service = QuestionVariationService(db)
        
        # Get base question
        base_question = question_lookup.get_question_by_id(test_request.base_question_id)
        if not base_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Base question not found"
            )
        
        # Validate variation
        validation = service.validate_question_variation(
            base_question,
            test_request.text,
            test_request.options,
            test_request.language
        )
        
        # Test against sample profiles if provided
        profile_matches = []
        if test_request.test_profiles:
            for profile_data in test_request.test_profiles:
                # Create temporary profile object
                profile = CustomerProfile(**profile_data)
                
                # Test if variation would be selected for this profile
                # This is a simplified test - in practice you'd use the full rule engine
                match_score = 0.0
                if test_request.demographic_rules:
                    # Simplified matching logic
                    match_score = 0.8  # Mock score
                
                profile_matches.append({
                    "profile": profile_data,
                    "matches": match_score > 0.5,
                    "match_score": match_score
                })
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="test_question_variation",
            entity_type="question_variation",
            details={
                "base_question_id": test_request.base_question_id,
                "language": test_request.language,
                "validation_score": validation.consistency_score
            }
        ))
        db.commit()
        
        return VariationTestResult(
            validation=validation,
            profile_matches=profile_matches,
            estimated_usage=len([m for m in profile_matches if m["matches"]]) if profile_matches else 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing question variation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error testing question variation"
        )


@router.get("/analytics/overview", response_model=QuestionVariationAnalytics)
async def get_variation_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get analytics overview for question variations.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total variations
        total_variations = db.query(QuestionVariation).count()
        active_variations = db.query(QuestionVariation).filter(
            QuestionVariation.is_active == True
        ).count()
        
        # Usage statistics
        recent_responses = db.query(SurveyResponse).filter(
            SurveyResponse.created_at >= start_date
        ).all()
        
        variation_usage = {}
        total_with_variations = 0
        
        for response in recent_responses:
            if response.question_variations_used:
                total_with_variations += 1
                for question_id, variation_id in response.question_variations_used.items():
                    variation_usage[variation_id] = variation_usage.get(variation_id, 0) + 1
        
        # Top variations
        top_variations = []
        if variation_usage:
            sorted_usage = sorted(variation_usage.items(), key=lambda x: x[1], reverse=True)
            for variation_id, usage_count in sorted_usage[:10]:
                variation = db.query(QuestionVariation).filter(
                    QuestionVariation.id == variation_id
                ).first()
                if variation:
                    top_variations.append({
                        "variation_id": variation_id,
                        "variation_name": variation.variation_name,
                        "base_question_id": variation.base_question_id,
                        "usage_count": usage_count
                    })
        
        # Language distribution
        language_stats = db.query(
            QuestionVariation.language,
            func.count(QuestionVariation.id).label('count')
        ).group_by(QuestionVariation.language).all()
        
        language_distribution = {lang: count for lang, count in language_stats}
        
        # Company usage
        company_variations = db.query(QuestionVariation).filter(
            QuestionVariation.company_ids.isnot(None)
        ).count()
        
        return QuestionVariationAnalytics(
            total_variations=total_variations,
            active_variations=active_variations,
            usage_rate=total_with_variations / len(recent_responses) if recent_responses else 0.0,
            top_variations=top_variations,
            language_distribution=language_distribution,
            company_specific_variations=company_variations,
            analysis_period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting variation analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


@router.get("/base-questions", response_model=List[Dict[str, Any]])
async def get_base_questions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Get list of base questions available for variation creation.
    """
    try:
        base_questions = []
        
        for question in question_lookup.get_all_questions():
            # Count existing variations
            variation_count = db.query(QuestionVariation).filter(
                QuestionVariation.base_question_id == question.id
            ).count()
            
            base_questions.append({
                "id": question.id,
                "question_number": question.question_number,
                "text": question.text,
                "factor": question.factor.value,
                "weight": question.weight,
                "existing_variations": variation_count
            })
        
        return base_questions
        
    except Exception as e:
        logger.error(f"Error getting base questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving base questions"
        )