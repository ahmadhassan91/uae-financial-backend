"""Routes for managing incomplete survey sessions."""
from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models import User, CustomerProfile, IncompleteSurvey, AuditLog
from app.surveys.incomplete_schemas import (
    IncompleteSurveyCreate, IncompleteSurveyUpdate, IncompleteSurveyResponse,
    IncompleteSurveyStats, FollowUpRequest
)
from app.auth.dependencies import get_current_user, get_current_admin_user
import secrets

router = APIRouter(prefix="/surveys/incomplete", tags=["incomplete-surveys"])


@router.post("/start", response_model=IncompleteSurveyResponse)
async def start_incomplete_survey(
    survey_data: IncompleteSurveyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Start tracking an incomplete survey session."""
    # Generate unique session ID
    session_id = secrets.token_urlsafe(32)
    
    # Get user's customer profile if exists
    customer_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    # Create incomplete survey record
    incomplete_survey = IncompleteSurvey(
        user_id=current_user.id,
        customer_profile_id=customer_profile.id if customer_profile else None,
        session_id=session_id,
        current_step=survey_data.current_step,
        total_steps=survey_data.total_steps,
        responses=survey_data.responses or {},
        email=survey_data.email or current_user.email
    )
    
    db.add(incomplete_survey)
    db.commit()
    db.refresh(incomplete_survey)
    
    # Log survey start
    audit_log = AuditLog(
        user_id=current_user.id,
        action="survey_started",
        entity_type="incomplete_survey",
        entity_id=incomplete_survey.id,
        details={"session_id": session_id, "total_steps": survey_data.total_steps}
    )
    db.add(audit_log)
    db.commit()
    
    return incomplete_survey


@router.post("/start-guest", response_model=IncompleteSurveyResponse)
async def start_guest_incomplete_survey(
    survey_data: IncompleteSurveyCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Start tracking an incomplete survey session for guest users."""
    # Generate unique session ID
    session_id = secrets.token_urlsafe(32)
    
    # Create incomplete survey record for guest
    incomplete_survey = IncompleteSurvey(
        session_id=session_id,
        current_step=survey_data.current_step,
        total_steps=survey_data.total_steps,
        responses=survey_data.responses or {},
        email=survey_data.email,
        phone_number=survey_data.phone_number
    )
    
    db.add(incomplete_survey)
    db.commit()
    db.refresh(incomplete_survey)
    
    # Log guest survey start
    audit_log = AuditLog(
        action="guest_survey_started",
        entity_type="incomplete_survey",
        entity_id=incomplete_survey.id,
        details={
            "session_id": session_id, 
            "total_steps": survey_data.total_steps,
            "email": survey_data.email
        }
    )
    db.add(audit_log)
    db.commit()
    
    return incomplete_survey


@router.put("/{session_id}", response_model=IncompleteSurveyResponse)
async def update_incomplete_survey(
    session_id: str,
    survey_data: IncompleteSurveyUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """Update progress on an incomplete survey session."""
    # Find the incomplete survey
    incomplete_survey = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.session_id == session_id,
        IncompleteSurvey.is_abandoned == False
    ).first()
    
    if not incomplete_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incomplete survey session not found"
        )
    
    # Update fields
    if survey_data.current_step is not None:
        incomplete_survey.current_step = survey_data.current_step
    
    if survey_data.responses is not None:
        # Merge responses
        existing_responses = incomplete_survey.responses or {}
        existing_responses.update(survey_data.responses)
        incomplete_survey.responses = existing_responses
    
    if survey_data.email is not None:
        incomplete_survey.email = survey_data.email
    
    if survey_data.phone_number is not None:
        incomplete_survey.phone_number = survey_data.phone_number
    
    # Update last activity
    incomplete_survey.last_activity = datetime.utcnow()
    
    db.commit()
    db.refresh(incomplete_survey)
    
    return incomplete_survey


@router.delete("/{session_id}")
async def complete_survey_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Mark a survey session as completed (remove from incomplete tracking)."""
    incomplete_survey = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.session_id == session_id
    ).first()
    
    if incomplete_survey:
        # Log completion
        audit_log = AuditLog(
            user_id=incomplete_survey.user_id,
            action="survey_completed_from_incomplete",
            entity_type="incomplete_survey",
            entity_id=incomplete_survey.id,
            details={"session_id": session_id}
        )
        db.add(audit_log)
        
        # Remove from incomplete tracking
        db.delete(incomplete_survey)
        db.commit()
    
    return {"message": "Survey session completed"}


# Admin routes
@router.get("/admin/list", response_model=List[IncompleteSurveyResponse])
async def list_incomplete_surveys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    abandoned_only: bool = Query(False),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """List incomplete surveys for admin review."""
    query = db.query(IncompleteSurvey)
    
    if abandoned_only:
        # Consider surveys abandoned if no activity for 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(
            and_(
                IncompleteSurvey.last_activity < cutoff_time,
                IncompleteSurvey.is_abandoned == False
            )
        )
        
        # Mark them as abandoned
        abandoned_surveys = query.all()
        for survey in abandoned_surveys:
            survey.is_abandoned = True
            survey.abandoned_at = datetime.utcnow()
        
        if abandoned_surveys:
            db.commit()
    
    # Apply filters
    if abandoned_only:
        query = query.filter(IncompleteSurvey.is_abandoned == True)
    
    # Order by most recent activity
    incomplete_surveys = query.order_by(
        IncompleteSurvey.last_activity.desc()
    ).offset(skip).limit(limit).all()
    
    return incomplete_surveys


@router.get("/admin/stats", response_model=IncompleteSurveyStats)
async def get_incomplete_survey_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get statistics about incomplete surveys."""
    # Total incomplete surveys
    total_incomplete = db.query(IncompleteSurvey).count()
    
    # Abandoned surveys (no activity for 24+ hours)
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    abandoned_count = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.last_activity < cutoff_time
    ).count()
    
    # Average completion rate (current_step / total_steps)
    from sqlalchemy import Float
    avg_completion = db.query(
        func.avg(
            func.cast(IncompleteSurvey.current_step, Float) / 
            func.cast(IncompleteSurvey.total_steps, Float) * 100
        )
    ).scalar() or 0.0
    
    # Most common exit step
    most_common_exit = db.query(
        IncompleteSurvey.current_step,
        func.count(IncompleteSurvey.current_step).label('count')
    ).group_by(IncompleteSurvey.current_step).order_by(
        func.count(IncompleteSurvey.current_step).desc()
    ).first()
    
    most_common_exit_step = most_common_exit[0] if most_common_exit else 0
    
    # Follow-up pending
    follow_up_pending = db.query(IncompleteSurvey).filter(
        and_(
            IncompleteSurvey.is_abandoned == True,
            IncompleteSurvey.follow_up_sent == False,
            IncompleteSurvey.email.isnot(None)
        )
    ).count()
    
    return IncompleteSurveyStats(
        total_incomplete=total_incomplete,
        abandoned_count=abandoned_count,
        average_completion_rate=round(avg_completion, 2),
        most_common_exit_step=most_common_exit_step,
        follow_up_pending=follow_up_pending
    )


@router.post("/admin/follow-up")
async def send_follow_up(
    follow_up_data: FollowUpRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Send follow-up communications to users with incomplete surveys."""
    # Get the incomplete surveys
    surveys = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.id.in_(follow_up_data.survey_ids)
    ).all()
    
    if not surveys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No surveys found with provided IDs"
        )
    
    sent_count = 0
    
    for survey in surveys:
        if not survey.email and follow_up_data.send_email:
            continue  # Skip if no email and email is requested
        
        # Here you would integrate with your email/SMS service
        # For now, we'll just mark as sent and log
        
        survey.follow_up_sent = True
        survey.follow_up_count += 1
        
        # Log follow-up
        audit_log = AuditLog(
            user_id=current_user.id,
            action="follow_up_sent",
            entity_type="incomplete_survey",
            entity_id=survey.id,
            details={
                "session_id": survey.session_id,
                "email": survey.email,
                "follow_up_count": survey.follow_up_count,
                "message_template": follow_up_data.message_template[:100]  # Truncate for logging
            }
        )
        db.add(audit_log)
        sent_count += 1
    
    db.commit()
    
    return {
        "message": f"Follow-up sent to {sent_count} users",
        "sent_count": sent_count,
        "total_requested": len(follow_up_data.survey_ids)
    }