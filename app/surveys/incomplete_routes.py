"""Routes for managing incomplete survey sessions."""
from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_, or_
import csv
import io
from app.database import get_db
from app.models import User, CustomerProfile, IncompleteSurvey, AuditLog, CompanyTracker
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
    
    # Get company if company_url provided
    company_id = None
    if survey_data.company_url:
        company = db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == survey_data.company_url,
            CompanyTracker.is_active == True
        ).first()
        if company:
            company_id = company.id
    
    # Create incomplete survey record
    incomplete_survey = IncompleteSurvey(
        user_id=current_user.id,
        customer_profile_id=customer_profile.id if customer_profile else None,
        session_id=session_id,
        current_step=survey_data.current_step,
        total_steps=survey_data.total_steps,
        responses=survey_data.responses or {},
        email=survey_data.email or current_user.email,
        company_id=company_id,
        company_url=survey_data.company_url
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
    
    # Get company if company_url provided
    company_id = None
    if survey_data.company_url:
        company = db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == survey_data.company_url,
            CompanyTracker.is_active == True
        ).first()
        if company:
            company_id = company.id
    
    # Create incomplete survey record for guest
    incomplete_survey = IncompleteSurvey(
        session_id=session_id,
        current_step=survey_data.current_step,
        total_steps=survey_data.total_steps,
        responses=survey_data.responses or {},
        email=survey_data.email,
        phone_number=survey_data.phone_number,
        company_id=company_id,
        company_url=survey_data.company_url
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
@router.patch("/{session_id}", response_model=IncompleteSurveyResponse)
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
        print(f"📝 Updating step from {incomplete_survey.current_step} to {survey_data.current_step}")
        incomplete_survey.current_step = survey_data.current_step
    
    if survey_data.responses is not None:
        # Merge responses
        existing_responses = incomplete_survey.responses or {}
        print(f"📝 Existing responses: {len(existing_responses)} questions")
        print(f"📝 New responses: {len(survey_data.responses)} questions")
        print(f"📝 New responses data: {survey_data.responses}")
        
        existing_responses.update(survey_data.responses)
        incomplete_survey.responses = existing_responses
        
        # Mark the JSON field as modified so SQLAlchemy detects the change
        flag_modified(incomplete_survey, 'responses')
        
        print(f"📝 After merge: {len(existing_responses)} total questions")
        print(f"📝 Question IDs: {list(existing_responses.keys())}")
    
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
    # First, auto-mark surveys as abandoned if they have no activity for 24+ hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    surveys_to_mark = db.query(IncompleteSurvey).filter(
        and_(
            IncompleteSurvey.last_activity < cutoff_time,
            IncompleteSurvey.is_abandoned == False
        )
    ).all()
    
    # Mark them as abandoned
    for survey in surveys_to_mark:
        survey.is_abandoned = True
        survey.abandoned_at = datetime.utcnow()
    
    if surveys_to_mark:
        db.commit()

    # Clean up duplicate sessions - keep only the most progressed session per user/email
    # Get all incomplete surveys grouped by user_id and email
    all_surveys = db.query(IncompleteSurvey).all()
    user_surveys = {}
    
    for survey in all_surveys:
        # Group by user_id (for registered users) or email (for guest users)
        key = survey.user_id if survey.user_id else survey.email
        if key not in user_surveys:
            user_surveys[key] = []
        user_surveys[key].append(survey)
    
    # For each user/email, keep only the survey with highest progress
    surveys_to_keep = []
    surveys_to_delete = []
    
    for key, surveys in user_surveys.items():
        if len(surveys) > 1:
            # Sort by progress (current_step/total_steps) then by last_activity
            surveys.sort(key=lambda s: (s.current_step / s.total_steps if s.total_steps > 0 else 0, s.last_activity), reverse=True)
            surveys_to_keep.append(surveys[0])  # Keep the most progressed
            surveys_to_delete.extend(surveys[1:])  # Delete the rest
        else:
            surveys_to_keep.append(surveys[0])
    
    # Delete duplicate sessions
    for survey in surveys_to_delete:
        db.delete(survey)
    
    if surveys_to_delete:
        db.commit()
        print(f"🧹 Cleaned up {len(surveys_to_delete)} duplicate survey sessions")
    
    # Now build the query for listing from remaining surveys
    query = db.query(IncompleteSurvey)
    
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
    # First, auto-mark surveys as abandoned if they have no activity for 24+ hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    surveys_to_mark = db.query(IncompleteSurvey).filter(
        and_(
            IncompleteSurvey.last_activity < cutoff_time,
            IncompleteSurvey.is_abandoned == False
        )
    ).all()
    
    # Mark them as abandoned
    for survey in surveys_to_mark:
        survey.is_abandoned = True
        survey.abandoned_at = datetime.utcnow()
    
    if surveys_to_mark:
        db.commit()
    
    # Total incomplete surveys
    total_incomplete = db.query(IncompleteSurvey).count()
    
    # Abandoned surveys (using is_abandoned flag)
    abandoned_count = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.is_abandoned == True
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
    from app.reports.email_service import EmailReportService
    from app.config import settings
    
    # Get the incomplete surveys
    surveys = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.id.in_(follow_up_data.survey_ids)
    ).all()
    
    if not surveys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No surveys found with provided IDs"
        )
    
    email_service = EmailReportService()
    sent_count = 0
    failed_count = 0
    
    for survey in surveys:
        if not survey.email and follow_up_data.send_email:
            continue  # Skip if no email and email is requested
        
        try:
            # Generate resume link with session_id (company-aware)
            frontend_url = settings.base_url
            
            # If survey was started via company, include company URL in resume link
            if survey.company_url:
                resume_link = f"{frontend_url}/company/{survey.company_url}/financial-clinic?session={survey.session_id}"
            else:
                resume_link = f"{frontend_url}/financial-clinic?session={survey.session_id}"
            
            # Extract customer name from email or use generic
            customer_name = survey.email.split('@')[0] if survey.email else "Valued Customer"
            
            # Detect language from responses if available
            language = "en"
            if survey.responses and isinstance(survey.responses, dict):
                language = survey.responses.get('language', 'en')
            
            # Send reminder email
            if follow_up_data.send_email and survey.email:
                result = await email_service.send_reminder_email(
                    recipient_email=survey.email,
                    customer_name=customer_name,
                    language=language,
                    resume_link=resume_link
                )
                
                if result.get('success'):
                    survey.follow_up_sent = True
                    survey.follow_up_count += 1
                    sent_count += 1
                else:
                    failed_count += 1
            
            # Log follow-up attempt
            audit_log = AuditLog(
                user_id=current_user.id,
                action="follow_up_sent",
                entity_type="incomplete_survey",
                entity_id=survey.id,
                details={
                    "session_id": survey.session_id,
                    "email": survey.email,
                    "company_url": survey.company_url,  # Track company context
                    "follow_up_count": survey.follow_up_count,
                    "resume_link": resume_link,
                    "message_template": follow_up_data.message_template[:100]  # Truncate for logging
                }
            )
            db.add(audit_log)
            
        except Exception as e:
            failed_count += 1
            print(f"Failed to send follow-up to {survey.email}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"Follow-up sent to {sent_count} users ({failed_count} failed)",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_requested": len(follow_up_data.survey_ids)
    }


@router.get("/resume/{session_id}", response_model=IncompleteSurveyResponse)
async def resume_survey_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Resume an incomplete survey session."""
    # Find the incomplete survey by session_id
    incomplete_survey = db.query(IncompleteSurvey).filter(
        IncompleteSurvey.session_id == session_id
    ).first()
    
    if not incomplete_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey session not found"
        )
    
    # Check if the survey is too old (30+ days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Handle timezone-aware vs timezone-naive comparison
    started_at = incomplete_survey.started_at
    if hasattr(started_at, 'tzinfo') and started_at.tzinfo is not None:
        started_at = started_at.replace(tzinfo=None)
        
    if started_at < thirty_days_ago:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Survey session has expired"
        )
    
    # Update last activity to current time
    incomplete_survey.last_activity = datetime.utcnow()
    db.commit()
    
    # Log the resume action
    audit_log = AuditLog(
        user_id=incomplete_survey.user_id,
        action="survey_resumed",
        entity_type="incomplete_survey",
        entity_id=incomplete_survey.id,
        details={
            "session_id": session_id,
            "company_url": incomplete_survey.company_url,
            "current_step": incomplete_survey.current_step
        }
    )
    db.add(audit_log)
    db.commit()
    
    # Extract profile data from responses if available
    profile_data = None
    if incomplete_survey.responses and isinstance(incomplete_survey.responses, dict):
        # Look for profile data in responses
        profile_data = incomplete_survey.responses.get('profile')
        
        # If no direct profile, try to extract from common fields
        if not profile_data and any(key in incomplete_survey.responses for key in ['name', 'email', 'gender']):
            profile_data = {
                'name': incomplete_survey.responses.get('name', ''),
                'date_of_birth': incomplete_survey.responses.get('date_of_birth', ''),
                'gender': incomplete_survey.responses.get('gender', 'Male'),
                'nationality': incomplete_survey.responses.get('nationality', 'Emirati'),
                'children': incomplete_survey.responses.get('children', 0),
                'employment_status': incomplete_survey.responses.get('employment_status', 'Employed'),
                'income_range': incomplete_survey.responses.get('income_range', 'Below 5,000'),
                'emirate': incomplete_survey.responses.get('emirate', 'Dubai'),
                'email': incomplete_survey.responses.get('email', incomplete_survey.email or ''),
                'mobile_number': incomplete_survey.responses.get('mobile_number', incomplete_survey.phone_number or '')
            }
    
    # Return enhanced response with profile data
    return {
        **incomplete_survey.__dict__,
        "profile": profile_data
    }


@router.get("/admin/export")
async def export_incomplete_surveys(
    abandoned_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Export incomplete surveys data in CSV format."""
    
    # Build query
    query = db.query(IncompleteSurvey)
    
    if abandoned_only:
        # Only get surveys that are abandoned (24h+ since last activity)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(
            or_(
                IncompleteSurvey.last_activity < cutoff_time,
                IncompleteSurvey.is_abandoned == True
            )
        )
    
    # Get surveys with pagination
    surveys = query.order_by(IncompleteSurvey.started_at.desc()).offset(skip).limit(limit).all()
    
    return _export_as_csv(surveys, abandoned_only)


def _export_as_csv(surveys: List[IncompleteSurvey], abandoned_only: bool) -> StreamingResponse:
    """Export surveys as CSV file."""
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Headers
    headers = [
        'ID', 'Session ID', 'User Type', 'Email', 'Phone', 'Company URL', 'Company ID',
        'Current Step', 'Total Steps', 'Completion %', 'Started At', 'Last Activity',
        'Status', 'Hours Since Activity', 'Is Abandoned', 'Follow-up Sent', 
        'Follow-up Count', 'Responses Count'
    ]
    writer.writerow(headers)
    
    # Data rows
    for survey in surveys:
        # Calculate status - handle timezone awareness
        now = datetime.utcnow()
        # Ensure both datetimes are offset-naive for comparison
        last_activity = survey.last_activity
        if hasattr(last_activity, 'tzinfo') and last_activity.tzinfo is not None:
            last_activity = last_activity.replace(tzinfo=None)
        
        hours_since_activity = (now - last_activity).total_seconds() / 3600
        
        if hours_since_activity < 24:
            status = 'Active'
        elif hours_since_activity < 72:
            status = 'Stalled'
        else:
            status = 'Abandoned'
        
        completion_pct = round((survey.current_step / survey.total_steps) * 100, 1)
        responses_count = len(survey.responses) if survey.responses else 0
        
        row = [
            survey.id,
            survey.session_id,
            'Registered' if survey.user_id else 'Guest',
            survey.email or '',
            survey.phone_number or '',
            survey.company_url or '',
            survey.company_id or '',
            survey.current_step,
            survey.total_steps,
            completion_pct,
            survey.started_at.isoformat(),
            survey.last_activity.isoformat(),
            status,
            round(hours_since_activity, 1),
            survey.is_abandoned,
            survey.follow_up_sent,
            survey.follow_up_count,
            responses_count
        ]
        writer.writerow(row)
    
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_suffix = "abandoned" if abandoned_only else "all"
    filename = f"incomplete_surveys_{filename_suffix}_{timestamp}.csv"
    
    # Return streaming response
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@router.post("/admin/cleanup-duplicates")
async def cleanup_duplicate_sessions(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Clean up duplicate survey sessions, keeping only the most progressed session per user."""
    
    # Get all incomplete surveys grouped by user_id and email
    all_surveys = db.query(IncompleteSurvey).all()
    user_surveys = {}
    
    for survey in all_surveys:
        # Group by user_id (for registered users) or email (for guest users)
        key = survey.user_id if survey.user_id else survey.email
        if key not in user_surveys:
            user_surveys[key] = []
        user_surveys[key].append(survey)
    
    # For each user/email, keep only the survey with highest progress
    surveys_to_delete = []
    duplicate_groups = 0
    
    for key, surveys in user_surveys.items():
        if len(surveys) > 1:
            duplicate_groups += 1
            # Sort by progress (current_step/total_steps) then by last_activity
            surveys.sort(key=lambda s: (
                s.current_step / s.total_steps if s.total_steps > 0 else 0, 
                s.last_activity
            ), reverse=True)
            
            # Keep the most progressed, delete the rest
            surveys_to_delete.extend(surveys[1:])
    
    # Delete duplicate sessions
    for survey in surveys_to_delete:
        db.delete(survey)
    
    if surveys_to_delete:
        db.commit()
    
    return {
        "message": f"Cleanup completed",
        "duplicate_groups_found": duplicate_groups,
        "sessions_removed": len(surveys_to_delete),
        "remaining_sessions": len(all_surveys) - len(surveys_to_delete)
    }

