"""Survey routes for managing financial health assessments."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, CustomerProfile, SurveyResponse, Recommendation, AuditLog
from app.surveys.schemas import (
    SurveyResponseCreate, SurveyResponseUpdate, SurveyResponseResponse,
    SurveyResultResponse, SurveyHistoryResponse, RecommendationResponse,
    ScoreBreakdown, ScorePreviewRequest, ScorePreviewResponse
)
from app.surveys.scoring import SurveyScorer
from app.surveys.recommendations import RecommendationEngine
from app.surveys.question_definitions import SURVEY_QUESTIONS_V2
from app.auth.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.get("/questions")
async def get_survey_questions(
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Get all available survey questions."""
    questions = []
    for q in SURVEY_QUESTIONS_V2:
        questions.append({
            "id": q.id,
            "question_number": q.question_number,
            "text": q.text,
            "type": q.type,
            "options": [{"value": opt.value, "label": opt.label} for opt in q.options],
            "required": q.required,
            "factor": q.factor.value,
            "weight": q.weight,
            "conditional": q.conditional
        })
    
    return questions


@router.post("/calculate-preview", response_model=ScorePreviewResponse)
async def calculate_score_preview(
    request: ScorePreviewRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Calculate score preview without saving to database (for real-time feedback)."""
    scorer = SurveyScorer()
    
    # Calculate scores using the v2 method with profile data
    result = scorer.calculate_scores_v2(request.responses, request.profile)
    
    # Convert pillar scores to the response format
    pillar_scores = []
    for pillar in result['pillar_scores']:
        pillar_scores.append({
            'factor': pillar['factor'],
            'name': pillar['name'],
            'score': pillar['score'],
            'max_score': pillar['max_score'],
            'percentage': pillar['percentage'],
            'weight': pillar['weight']
        })
    
    return ScorePreviewResponse(
        total_score=result['total_score'],
        max_possible_score=result['max_possible_score'],
        pillar_scores=pillar_scores,
        weighted_sum=result['weighted_sum'],
        total_weight=result['total_weight'],
        average_score=result['average_score']
    )


@router.post("/submit-guest", response_model=SurveyResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_guest_survey(
    survey_data: SurveyResponseCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Submit a survey response as a guest user (no authentication required)."""
    # Calculate scores using the scoring engine (guest users have no profile)
    scorer = SurveyScorer()
    scores_v2 = scorer.calculate_scores_v2(survey_data.responses, profile=None)
    scores = scorer.calculate_scores(survey_data.responses)  # Legacy format for compatibility
    risk_tolerance = scorer.determine_risk_tolerance(survey_data.responses)
    financial_goals = scorer.extract_financial_goals(survey_data.responses)
    
    # Generate personalized recommendations without saving to database
    recommendation_engine = RecommendationEngine()
    
    # Create a temporary survey response object for recommendation generation
    from datetime import datetime
    temp_survey = type('TempSurvey', (), {
        'id': 0,
        'user_id': 0,
        'customer_profile_id': 0,
        'overall_score': scores['overall_score'],
        'budgeting_score': scores['budgeting_score'],
        'savings_score': scores['savings_score'],
        'debt_management_score': scores['debt_management_score'],
        'financial_planning_score': scores['financial_planning_score'],
        'investment_knowledge_score': scores['investment_knowledge_score'],
        'risk_tolerance': risk_tolerance,
        'financial_goals': financial_goals,
        'responses': survey_data.responses,
        'completion_time': survey_data.completion_time,
        'survey_version': '1.0',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })()
    
    # Generate recommendations without customer profile
    recommendations_data = recommendation_engine.generate_recommendations(
        temp_survey, None  # No customer profile for guest users
    )
    
    # Create recommendation objects (not saved to database)
    recommendations = []
    for i, rec_data in enumerate(recommendations_data):
        rec_data.update({
            'id': i,
            'survey_response_id': 0,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        rec = type('TempRecommendation', (), rec_data)()
        recommendations.append(rec)
    
    # Log guest survey completion (without user_id)
    audit_log = AuditLog(
        action="guest_survey_completed",
        entity_type="guest_survey",
        details={
            "overall_score": scores['overall_score'],
            "risk_tolerance": risk_tolerance,
            "completion_time": survey_data.completion_time
        }
    )
    db.add(audit_log)
    db.commit()
    
    # Prepare response
    score_breakdown = ScoreBreakdown(
        overall_score=scores['overall_score'],
        budgeting_score=scores['budgeting_score'],
        savings_score=scores['savings_score'],
        debt_management_score=scores['debt_management_score'],
        financial_planning_score=scores['financial_planning_score'],
        investment_knowledge_score=scores['investment_knowledge_score'],
        risk_tolerance=risk_tolerance,
        financial_goals=financial_goals
    )
    
    return SurveyResultResponse(
        survey_response=temp_survey,
        recommendations=recommendations,
        score_breakdown=score_breakdown
    )


@router.post("/submit", response_model=SurveyResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_survey(
    survey_data: SurveyResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Submit a new survey response and get results with recommendations."""
    # Check if user has a customer profile
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not customer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer profile required before taking survey"
        )
    
    # Calculate scores using the scoring engine with profile data for conditional Q16
    scorer = SurveyScorer()
    profile_data = {'children': customer_profile.children}
    scores_v2 = scorer.calculate_scores_v2(survey_data.responses, profile=profile_data)
    scores = scorer.calculate_scores(survey_data.responses)  # Legacy format for compatibility
    risk_tolerance = scorer.determine_risk_tolerance(survey_data.responses)
    financial_goals = scorer.extract_financial_goals(survey_data.responses)
    
    # Create survey response record
    db_survey = SurveyResponse(
        user_id=current_user.id,
        customer_profile_id=customer_profile.id,
        responses=survey_data.responses,
        overall_score=scores['overall_score'],
        budgeting_score=scores['budgeting_score'],
        savings_score=scores['savings_score'],
        debt_management_score=scores['debt_management_score'],
        financial_planning_score=scores['financial_planning_score'],
        investment_knowledge_score=scores['investment_knowledge_score'],
        risk_tolerance=risk_tolerance,
        financial_goals=financial_goals,
        completion_time=survey_data.completion_time,
        survey_version="1.0"
    )
    
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    # Generate personalized recommendations
    recommendation_engine = RecommendationEngine()
    recommendations_data = recommendation_engine.generate_recommendations(
        db_survey, customer_profile
    )
    
    # Save recommendations to database
    db_recommendations = []
    for rec_data in recommendations_data:
        db_rec = Recommendation(
            survey_response_id=db_survey.id,
            **rec_data
        )
        db.add(db_rec)
        db_recommendations.append(db_rec)
    
    db.commit()
    
    # Refresh recommendations to get IDs
    for rec in db_recommendations:
        db.refresh(rec)
    
    # Log survey completion
    audit_log = AuditLog(
        user_id=current_user.id,
        action="survey_completed",
        entity_type="survey_response",
        entity_id=db_survey.id,
        details={
            "overall_score": db_survey.overall_score,
            "risk_tolerance": db_survey.risk_tolerance,
            "completion_time": db_survey.completion_time
        }
    )
    db.add(audit_log)
    db.commit()
    
    # Prepare response
    score_breakdown = ScoreBreakdown(
        overall_score=db_survey.overall_score,
        budgeting_score=db_survey.budgeting_score,
        savings_score=db_survey.savings_score,
        debt_management_score=db_survey.debt_management_score,
        financial_planning_score=db_survey.financial_planning_score,
        investment_knowledge_score=db_survey.investment_knowledge_score,
        risk_tolerance=db_survey.risk_tolerance,
        financial_goals=db_survey.financial_goals
    )
    
    return SurveyResultResponse(
        survey_response=db_survey,
        recommendations=db_recommendations,
        score_breakdown=score_breakdown
    )


@router.get("/results/{survey_id}", response_model=SurveyResultResponse)
async def get_survey_results(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get survey results and recommendations by survey ID."""
    # Get survey response
    survey = db.query(SurveyResponse).filter(
        SurveyResponse.id == survey_id,
        SurveyResponse.user_id == current_user.id
    ).first()
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey response not found"
        )
    
    # Get recommendations
    recommendations = db.query(Recommendation).filter(
        Recommendation.survey_response_id == survey_id,
        Recommendation.is_active == True
    ).all()
    
    # Prepare score breakdown
    score_breakdown = ScoreBreakdown(
        overall_score=survey.overall_score,
        budgeting_score=survey.budgeting_score,
        savings_score=survey.savings_score,
        debt_management_score=survey.debt_management_score,
        financial_planning_score=survey.financial_planning_score,
        investment_knowledge_score=survey.investment_knowledge_score,
        risk_tolerance=survey.risk_tolerance,
        financial_goals=survey.financial_goals
    )
    
    return SurveyResultResponse(
        survey_response=survey,
        recommendations=recommendations,
        score_breakdown=score_breakdown
    )


@router.get("/history", response_model=List[SurveyHistoryResponse])
async def get_survey_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's survey history."""
    surveys = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == current_user.id
    ).order_by(SurveyResponse.created_at.desc()).offset(skip).limit(limit).all()
    
    return surveys


@router.get("/latest", response_model=SurveyResultResponse)
async def get_latest_survey(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's latest survey results."""
    # Get latest survey response
    survey = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == current_user.id
    ).order_by(SurveyResponse.created_at.desc()).first()
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No survey responses found"
        )
    
    # Get recommendations
    recommendations = db.query(Recommendation).filter(
        Recommendation.survey_response_id == survey.id,
        Recommendation.is_active == True
    ).all()
    
    # Prepare score breakdown
    score_breakdown = ScoreBreakdown(
        overall_score=survey.overall_score,
        budgeting_score=survey.budgeting_score,
        savings_score=survey.savings_score,
        debt_management_score=survey.debt_management_score,
        financial_planning_score=survey.financial_planning_score,
        investment_knowledge_score=survey.investment_knowledge_score,
        risk_tolerance=survey.risk_tolerance,
        financial_goals=survey.financial_goals
    )
    
    return SurveyResultResponse(
        survey_response=survey,
        recommendations=recommendations,
        score_breakdown=score_breakdown
    )


@router.put("/responses/{survey_id}", response_model=SurveyResponseResponse)
async def update_survey_response(
    survey_id: int,
    survey_data: SurveyResponseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update an existing survey response (for draft surveys)."""
    survey = db.query(SurveyResponse).filter(
        SurveyResponse.id == survey_id,
        SurveyResponse.user_id == current_user.id
    ).first()
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey response not found"
        )
    
    # Update provided fields
    update_data = survey_data.dict(exclude_unset=True)
    
    # If responses are updated, recalculate scores
    if 'responses' in update_data:
        scorer = SurveyScorer()
        scores = scorer.calculate_scores(update_data['responses'])
        risk_tolerance = scorer.determine_risk_tolerance(update_data['responses'])
        financial_goals = scorer.extract_financial_goals(update_data['responses'])
        
        # Update calculated fields
        update_data.update(scores)
        update_data['risk_tolerance'] = risk_tolerance
        update_data['financial_goals'] = financial_goals
    
    # Apply updates
    for field, value in update_data.items():
        setattr(survey, field, value)
    
    db.commit()
    db.refresh(survey)
    
    # Log survey update
    audit_log = AuditLog(
        user_id=current_user.id,
        action="survey_updated",
        entity_type="survey_response",
        entity_id=survey.id,
        details={"updated_fields": list(update_data.keys())}
    )
    db.add(audit_log)
    db.commit()
    
    return survey


# Admin routes
@router.get("/admin/all", response_model=List[SurveyResponseResponse])
async def list_all_surveys(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all survey responses (admin only)."""
    surveys = db.query(SurveyResponse).offset(skip).limit(limit).all()
    return surveys


@router.get("/admin/stats")
async def get_survey_statistics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get survey statistics for admin dashboard."""
    total_surveys = db.query(SurveyResponse).count()
    
    # Calculate average scores
    avg_scores = db.query(
        db.func.avg(SurveyResponse.overall_score).label('avg_overall'),
        db.func.avg(SurveyResponse.budgeting_score).label('avg_budgeting'),
        db.func.avg(SurveyResponse.savings_score).label('avg_savings'),
        db.func.avg(SurveyResponse.debt_management_score).label('avg_debt'),
        db.func.avg(SurveyResponse.financial_planning_score).label('avg_planning'),
        db.func.avg(SurveyResponse.investment_knowledge_score).label('avg_investment')
    ).first()
    
    # Risk tolerance distribution
    risk_distribution = db.query(
        SurveyResponse.risk_tolerance,
        db.func.count(SurveyResponse.id).label('count')
    ).group_by(SurveyResponse.risk_tolerance).all()
    
    return {
        "total_surveys": total_surveys,
        "average_scores": {
            "overall": round(avg_scores.avg_overall or 0, 2),
            "budgeting": round(avg_scores.avg_budgeting or 0, 2),
            "savings": round(avg_scores.avg_savings or 0, 2),
            "debt_management": round(avg_scores.avg_debt or 0, 2),
            "financial_planning": round(avg_scores.avg_planning or 0, 2),
            "investment_knowledge": round(avg_scores.avg_investment or 0, 2)
        },
        "risk_tolerance_distribution": {
            item.risk_tolerance: item.count for item in risk_distribution
        }
    }
