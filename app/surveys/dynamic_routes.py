"""
API routes for dynamic question selection and demographic rule management.

This module provides REST endpoints for the dynamic question engine,
allowing clients to get personalized question sets and manage rules.
"""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import CustomerProfile, DemographicRule, QuestionVariation
from app.surveys.demographic_rule_engine import DemographicRuleEngine
from app.surveys.question_variation_service import QuestionVariationService
from app.surveys.dynamic_question_engine import (
    DynamicQuestionEngine, QuestionSelectionStrategy
)
from app.surveys.sample_demographic_data import populate_sample_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dynamic-questions", tags=["Dynamic Questions"])


# Pydantic models for API
class QuestionOptionResponse(BaseModel):
    value: int
    label: str


class QuestionResponse(BaseModel):
    id: str
    question_number: int
    text: str
    type: str
    options: List[QuestionOptionResponse]
    required: bool
    factor: str
    weight: int
    conditional: bool = False


class DynamicQuestionSetResponse(BaseModel):
    questions: List[QuestionResponse]
    variations_used: Dict[str, int]
    selection_metadata: Dict[str, Any]
    strategy_used: str
    total_questions: int
    generated_at: str


class RuleEvaluationResponse(BaseModel):
    rule_id: int
    rule_name: str
    matched: bool
    actions: Dict[str, Any]
    priority: int


class DemographicAnalysisResponse(BaseModel):
    profile_id: int
    matched_rules: List[RuleEvaluationResponse]
    selected_questions: List[str]
    excluded_questions: List[str]
    added_questions: List[str]
    demographic_profile_hash: str


class QuestionVariationResponse(BaseModel):
    id: int
    base_question_id: str
    variation_name: str
    language: str
    text: str
    options: List[Dict[str, Any]]
    demographic_rules: Optional[Dict[str, Any]]
    company_ids: Optional[List[int]]
    factor: str
    weight: int
    is_active: bool


class CreateVariationRequest(BaseModel):
    base_question_id: str
    variation_name: str
    text: str
    options: List[Dict[str, Any]]
    language: str = "en"
    demographic_rules: Optional[Dict[str, Any]] = None
    company_ids: Optional[List[int]] = None


class RuleValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]


@router.get("/questions/{profile_id}", response_model=DynamicQuestionSetResponse)
async def get_questions_for_profile(
    profile_id: int,
    strategy: QuestionSelectionStrategy = Query(QuestionSelectionStrategy.HYBRID),
    language: str = Query("en", description="Language code (en, ar)"),
    company_id: Optional[int] = Query(None, description="Company ID for company-specific questions"),
    force_refresh: bool = Query(False, description="Force cache refresh"),
    db: Session = Depends(get_db)
):
    """
    Get personalized question set for a customer profile.
    
    This endpoint uses the dynamic question engine to select the most appropriate
    questions based on the user's demographic profile and company context.
    """
    try:
        # Get customer profile
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.id == profile_id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        
        # Initialize dynamic question engine
        question_engine = DynamicQuestionEngine(db)
        
        # Get question set
        question_set = await question_engine.get_questions_for_profile(
            profile=profile,
            company_id=company_id,
            language=language,
            strategy=strategy,
            force_refresh=force_refresh
        )
        
        # Convert to response format
        questions_response = []
        for q in question_set.questions:
            options_response = [
                QuestionOptionResponse(value=opt.value, label=opt.label)
                for opt in q.options
            ]
            
            questions_response.append(QuestionResponse(
                id=q.id,
                question_number=q.question_number,
                text=q.text,
                type=q.type,
                options=options_response,
                required=q.required,
                factor=q.factor.value,
                weight=q.weight,
                conditional=q.conditional
            ))
        
        return DynamicQuestionSetResponse(
            questions=questions_response,
            variations_used=question_set.variations_used,
            selection_metadata=question_set.selection_metadata,
            strategy_used=question_set.strategy_used.value,
            total_questions=len(questions_response),
            generated_at=question_set.generated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting questions for profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{profile_id}", response_model=DemographicAnalysisResponse)
async def analyze_demographic_profile(
    profile_id: int,
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Analyze a demographic profile and show which rules match.
    
    This endpoint provides detailed analysis of how demographic rules
    are applied to a specific customer profile.
    """
    try:
        # Get customer profile
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.id == profile_id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Customer profile not found")
        
        # Initialize rule engine
        rule_engine = DemographicRuleEngine(db)
        
        # Evaluate rules
        rule_results = rule_engine.evaluate_rules_for_profile(profile, company_id)
        
        # Get question selection
        selection_result = rule_engine.select_questions_for_profile(profile, company_id=company_id)
        
        # Convert rule results
        matched_rules = []
        for result in rule_results:
            matched_rules.append(RuleEvaluationResponse(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                matched=result.matched,
                actions=result.actions,
                priority=result.priority
            ))
        
        return DemographicAnalysisResponse(
            profile_id=profile_id,
            matched_rules=matched_rules,
            selected_questions=selection_result.selected_questions,
            excluded_questions=selection_result.excluded_questions,
            added_questions=selection_result.added_questions,
            demographic_profile_hash=selection_result.demographic_profile_hash
        )
        
    except Exception as e:
        logger.error(f"Error analyzing profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variations", response_model=List[QuestionVariationResponse])
async def get_question_variations(
    base_question_id: Optional[str] = Query(None),
    language: str = Query("en"),
    company_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get question variations based on criteria."""
    try:
        variation_service = QuestionVariationService(db)
        
        variations = variation_service.get_question_variations(
            base_question_id=base_question_id,
            language=language,
            company_id=company_id,
            active_only=active_only
        )
        
        return [
            QuestionVariationResponse(
                id=var.id,
                base_question_id=var.base_question_id,
                variation_name=var.variation_name,
                language=var.language,
                text=var.text,
                options=var.options,
                demographic_rules=var.demographic_rules,
                company_ids=var.company_ids,
                factor=var.factor,
                weight=var.weight,
                is_active=var.is_active
            )
            for var in variations
        ]
        
    except Exception as e:
        logger.error(f"Error getting question variations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variations", response_model=Dict[str, Any])
async def create_question_variation(
    request: CreateVariationRequest,
    db: Session = Depends(get_db)
):
    """Create a new question variation."""
    try:
        variation_service = QuestionVariationService(db)
        
        success, message, variation = variation_service.create_question_variation(
            base_question_id=request.base_question_id,
            variation_name=request.variation_name,
            text=request.text,
            options=request.options,
            language=request.language,
            demographic_rules=request.demographic_rules,
            company_ids=request.company_ids
        )
        
        if success:
            return {
                "success": True,
                "message": message,
                "variation_id": variation.id if variation else None
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question variation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=List[Dict[str, Any]])
async def get_demographic_rules(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all demographic rules."""
    try:
        query = db.query(DemographicRule)
        
        if active_only:
            query = query.filter(DemographicRule.is_active == True)
        
        rules = query.order_by(DemographicRule.priority.asc()).all()
        
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "created_at": rule.created_at.isoformat() if rule.created_at else None
            }
            for rule in rules
        ]
        
    except Exception as e:
        logger.error(f"Error getting demographic rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/validate", response_model=RuleValidationResponse)
async def validate_demographic_rule(
    rule_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Validate a demographic rule for compliance and correctness."""
    try:
        rule_engine = DemographicRuleEngine(db)
        validation = rule_engine.validate_rule(rule_data)
        
        return RuleValidationResponse(
            valid=validation['valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
        
    except Exception as e:
        logger.error(f"Error validating rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=Dict[str, Any])
async def get_question_analytics(
    db: Session = Depends(get_db)
):
    """Get analytics for question selection and variations."""
    try:
        # This would typically come from a cached analytics service
        # For now, return basic statistics
        
        total_rules = db.query(DemographicRule).filter(
            DemographicRule.is_active == True
        ).count()
        
        total_variations = db.query(QuestionVariation).filter(
            QuestionVariation.is_active == True
        ).count()
        
        variations_by_language = db.query(
            QuestionVariation.language,
            db.func.count(QuestionVariation.id)
        ).filter(
            QuestionVariation.is_active == True
        ).group_by(QuestionVariation.language).all()
        
        return {
            "total_active_rules": total_rules,
            "total_active_variations": total_variations,
            "variations_by_language": dict(variations_by_language),
            "cache_stats": {
                "note": "Cache statistics would be available with Redis integration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/populate-sample-data", response_model=Dict[str, Any])
async def populate_sample_demographic_data(
    db: Session = Depends(get_db)
):
    """Populate database with sample demographic rules and question variations."""
    try:
        result = populate_sample_data(db)
        return result
        
    except Exception as e:
        logger.error(f"Error populating sample data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache", response_model=Dict[str, Any])
async def clear_question_cache(
    pattern: Optional[str] = Query(None, description="Cache key pattern to clear"),
    db: Session = Depends(get_db)
):
    """Clear question selection cache."""
    try:
        question_engine = DynamicQuestionEngine(db)
        await question_engine.clear_cache(pattern)
        
        return {
            "success": True,
            "message": f"Cache cleared{' for pattern: ' + pattern if pattern else ''}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))