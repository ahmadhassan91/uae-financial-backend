"""API routes for consultation requests."""
from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import csv
import io
import logging

from app.database import get_db
from app.models import ConsultationRequest, AuditLog
from app.consultations.schemas import (
    ConsultationRequestCreate,
    ConsultationRequestUpdate, 
    ConsultationRequestResponse,
    ConsultationRequestStats,
    ConsultationRequestFilters
)
from app.auth.dependencies import get_current_admin_user, get_current_user
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("/request", response_model=ConsultationRequestResponse)
async def create_consultation_request(
    request_data: ConsultationRequestCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new consultation request (public endpoint)."""
    try:
        logger.info(f"📞 New consultation request from: {request_data.email}")
        
        # Check for duplicate requests within 24 hours
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        existing_request = db.query(ConsultationRequest).filter(
            and_(
                ConsultationRequest.email == request_data.email,
                ConsultationRequest.created_at >= recent_cutoff
            )
        ).first()
        
        if existing_request:
            logger.warning(f"⚠️ Duplicate consultation request from {request_data.email}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You have already submitted a consultation request recently. Please wait 24 hours before submitting another request."
            )
        
        # Create new consultation request
        consultation_request = ConsultationRequest(
            name=request_data.name,
            email=request_data.email,
            phone_number=request_data.phone_number,
            message=request_data.message,
            preferred_contact_method=request_data.preferred_contact_method,
            preferred_time=request_data.preferred_time,
            source=request_data.source
        )
        
        db.add(consultation_request)
        db.commit()
        db.refresh(consultation_request)
        
        # Log the request creation
        audit_log = AuditLog(
            action="consultation_request_created",
            entity_type="consultation_request",
            entity_id=consultation_request.id,
            details={
                "email": request_data.email,
                "name": request_data.name,
                "source": request_data.source,
                "preferred_contact": request_data.preferred_contact_method
            }
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Consultation request created: ID {consultation_request.id}")
        
        return consultation_request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating consultation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit consultation request. Please try again."
        )


# Admin endpoints
@router.get("/admin/list", response_model=List[ConsultationRequestResponse])
async def list_consultation_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    income_range: Optional[str] = Query(None),
    nationality: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    company_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """List consultation requests for admin review with demographic filters."""
    try:
        from app.models import FinancialClinicProfile, FinancialClinicResponse, CompanyTracker
        
        # Build base query - join with profile to enable demographic filtering
        query = db.query(ConsultationRequest).outerjoin(
            FinancialClinicProfile,
            ConsultationRequest.email == FinancialClinicProfile.email
        )
        
        # Apply consultation request filters
        if status:
            query = query.filter(ConsultationRequest.status == status)
        
        if source:
            query = query.filter(ConsultationRequest.source == source)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ConsultationRequest.name.ilike(search_term),
                    ConsultationRequest.email.ilike(search_term),
                    ConsultationRequest.phone_number.ilike(search_term)
                )
            )
        
        # Apply demographic filters (from profile)
        if income_range:
            query = query.filter(FinancialClinicProfile.income_range == income_range)
        
        if nationality:
            query = query.filter(FinancialClinicProfile.nationality == nationality)
        
        if company_id:
            # Join with FinancialClinicResponse to get company_tracker_id
            query = query.outerjoin(
                FinancialClinicResponse,
                FinancialClinicResponse.profile_id == FinancialClinicProfile.id
            ).filter(FinancialClinicResponse.company_tracker_id == company_id)
        
        # Order by most recent first and get results
        consultation_requests = query.order_by(
            desc(ConsultationRequest.created_at)
        ).offset(skip).limit(limit).all()
        
        # Apply age filtering in Python if needed
        if age_group:
            def calculate_age(dob_str):
                if not dob_str:
                    return None
                try:
                    dob = datetime.strptime(dob_str.strip(), '%d/%m/%Y')
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return age
                except:
                    return None
            
            # Filter results by age
            filtered_requests = []
            for request in consultation_requests:
                # Get profile for this request
                profile = db.query(FinancialClinicProfile).filter(
                    FinancialClinicProfile.email == request.email
                ).first()
                
                if not profile or not profile.date_of_birth:
                    continue
                
                age = calculate_age(profile.date_of_birth)
                if age is None:
                    continue
                
                if age_group == "< 18" and age < 18:
                    filtered_requests.append(request)
                elif age_group == "18-25" and 18 <= age <= 25:
                    filtered_requests.append(request)
                elif age_group == "26-35" and 26 <= age <= 35:
                    filtered_requests.append(request)
                elif age_group == "36-45" and 36 <= age <= 45:
                    filtered_requests.append(request)
                elif age_group == "46-60" and 46 <= age <= 60:
                    filtered_requests.append(request)
                elif age_group == "60+" and age > 60:
                    filtered_requests.append(request)
            
            consultation_requests = filtered_requests
        
        return consultation_requests
        
    except Exception as e:
        logger.error(f"❌ Error listing consultation requests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consultation requests"
        )


@router.get("/admin/stats", response_model=ConsultationRequestStats)
async def get_consultation_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get consultation request statistics."""
    try:
        # Total requests
        total = db.query(ConsultationRequest).count()
        
        # Requests by status
        pending = db.query(ConsultationRequest).filter(
            ConsultationRequest.status == "pending"
        ).count()
        
        contacted = db.query(ConsultationRequest).filter(
            ConsultationRequest.status == "contacted"
        ).count()
        
        scheduled = db.query(ConsultationRequest).filter(
            ConsultationRequest.status == "scheduled"
        ).count()
        
        completed = db.query(ConsultationRequest).filter(
            ConsultationRequest.status == "completed"
        ).count()
        
        # This week's requests (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week = db.query(ConsultationRequest).filter(
            ConsultationRequest.created_at >= week_ago
        ).count()
        
        # Conversion rate (scheduled + completed / total)
        conversion_count = scheduled + completed
        conversion_rate = (conversion_count / total * 100) if total > 0 else 0.0
        
        return ConsultationRequestStats(
            total=total,
            pending=pending,
            contacted=contacted,
            scheduled=scheduled,
            completed=completed,
            this_week=this_week,
            conversion_rate=round(conversion_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting consultation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consultation statistics"
        )


@router.put("/admin/{request_id}", response_model=ConsultationRequestResponse)
async def update_consultation_request(
    request_id: int,
    update_data: ConsultationRequestUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a consultation request (admin only)."""
    try:
        consultation_request = db.query(ConsultationRequest).filter(
            ConsultationRequest.id == request_id
        ).first()
        
        if not consultation_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation request not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(consultation_request, field, value)
        
        # Set timestamps based on status changes
        if update_data.status == "contacted" and not consultation_request.contacted_at:
            consultation_request.contacted_at = datetime.utcnow()
        elif update_data.status == "scheduled" and update_data.scheduled_at:
            consultation_request.scheduled_at = update_data.scheduled_at
        
        consultation_request.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(consultation_request)
        
        # Log the update
        audit_log = AuditLog(
            user_id=current_user.id,
            action="consultation_request_updated",
            entity_type="consultation_request",
            entity_id=consultation_request.id,
            details={
                "updated_fields": list(update_dict.keys()),
                "new_status": update_data.status,
                "admin_email": current_user.email
            }
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Consultation request {request_id} updated by {current_user.email}")
        
        return consultation_request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating consultation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consultation request"
        )


@router.delete("/admin/{request_id}")
async def delete_consultation_request(
    request_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a consultation request (admin only)."""
    try:
        consultation_request = db.query(ConsultationRequest).filter(
            ConsultationRequest.id == request_id
        ).first()
        
        if not consultation_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation request not found"
            )
        
        # Log the deletion before removing
        audit_log = AuditLog(
            user_id=current_user.id,
            action="consultation_request_deleted",
            entity_type="consultation_request",
            entity_id=consultation_request.id,
            details={
                "email": consultation_request.email,
                "name": consultation_request.name,
                "admin_email": current_user.email
            }
        )
        db.add(audit_log)
        
        # Delete the request
        db.delete(consultation_request)
        db.commit()
        
        logger.info(f"✅ Consultation request {request_id} deleted by {current_user.email}")
        
        return {"message": "Consultation request deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting consultation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete consultation request"
        )


@router.get("/admin/export")
async def export_consultation_requests_csv(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """Export consultation requests as CSV with comprehensive Financial Clinic data (admin only)."""
    try:
        from app.models import FinancialClinicProfile, FinancialClinicResponse
        from sqlalchemy import and_
        from sqlalchemy.sql import func
        
        # First, get the most recent response ID for each profile
        subquery = db.query(
            FinancialClinicResponse.profile_id,
            func.max(FinancialClinicResponse.id).label('max_response_id')
        ).group_by(FinancialClinicResponse.profile_id).subquery()
        
        # Build query with filters - join with Financial Clinic data
        # Join to get the most recent response for each profile
        query = db.query(
            ConsultationRequest,
            FinancialClinicProfile,
            FinancialClinicResponse
        ).outerjoin(
            FinancialClinicProfile,
            ConsultationRequest.email == FinancialClinicProfile.email
        ).outerjoin(
            subquery,
            FinancialClinicProfile.id == subquery.c.profile_id
        ).outerjoin(
            FinancialClinicResponse,
            and_(
                FinancialClinicResponse.id == subquery.c.max_response_id,
                FinancialClinicResponse.profile_id == FinancialClinicProfile.id
            )
        )
        
        if status:
            query = query.filter(ConsultationRequest.status == status)
        
        if source:
            query = query.filter(ConsultationRequest.source == source)
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.filter(ConsultationRequest.created_at >= date_from_dt)
        
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.filter(ConsultationRequest.created_at <= date_to_dt)
        
        # Get all matching requests with their related data
        results = query.order_by(desc(ConsultationRequest.created_at)).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write comprehensive header matching the reference CSV structure
        writer.writerow([
            # Consultation Request Fields
            'Consultation ID', 'Consultation Status', 'Consultation Source',
            'Preferred Contact Method', 'Preferred Time', 'Message',
            'Consultation Created At', 'Contacted At', 'Scheduled At', 'Notes',
            
            # Profile Information (matches Financial Clinic export)
            'Profile ID', 'Name', 'Email', 'Mobile Number', 'Date of Birth', 'Age',
            'Gender', 'Nationality', 'Emirate', 'Children',
            'Employment Status', 'Income Range', 'Company',
            
            # Assessment Results
            'Response ID', 'Total Score', 'Status Band', 'Questions Answered', 'Total Questions',
            
            # Category Scores
            'Income Stream Score', 'Savings Habit Score', 'Debt Management Score',
            'Retirement Planning Score', 'Financial Protection Score', 'Financial Knowledge Score',
            
            # Submission Date
            'Assessment Submission Date'
        ])
        
        # Helper function to calculate age from DOB string (DD/MM/YYYY)
        def calculate_age(dob_str):
            if not dob_str or dob_str.strip() == '':
                return ''
            try:
                from datetime import datetime
                # Try DD/MM/YYYY format first
                dob = datetime.strptime(dob_str.strip(), '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return age
            except ValueError:
                # Try YYYY-MM-DD format (ISO format)
                try:
                    dob = datetime.strptime(dob_str.strip(), '%Y-%m-%d')
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return age
                except:
                    return ''
            except:
                return ''
        
        # Helper function to get category score from JSON
        def get_category_score(category_scores, category_name):
            if not category_scores:
                return 0
            try:
                # category_scores is stored as JSON with structure like:
                # {"income_stream": {"score": 10, ...}, "savings_habit": {...}, ...}
                if isinstance(category_scores, dict):
                    category_data = category_scores.get(category_name, {})
                    if isinstance(category_data, dict):
                        return round(category_data.get('score', 0), 2)
                    # Fallback: check if it's stored differently
                    elif isinstance(category_data, (int, float)):
                        return round(float(category_data), 2)
                return 0
            except Exception as e:
                logger.warning(f"Error extracting category score for {category_name}: {e}")
                return 0
        
        # Write data rows
        for request, profile, response in results:
            # Debug logging for first record
            if request.id == results[0][0].id and response:
                logger.info(f"🔍 Debug - Response ID: {response.id}, category_scores type: {type(response.category_scores)}")
                logger.info(f"🔍 Debug - category_scores content: {response.category_scores}")
            
            # Extract category scores if response exists
            # NOTE: Category keys use spaces, not snake_case (e.g., "Income Stream" not "income_stream")
            income_stream_score = get_category_score(response.category_scores if response else None, 'Income Stream')
            savings_habit_score = get_category_score(response.category_scores if response else None, 'Savings Habit')
            debt_management_score = get_category_score(response.category_scores if response else None, 'Debt Management')
            retirement_planning_score = get_category_score(response.category_scores if response else None, 'Retirement Planning')
            financial_protection_score = get_category_score(response.category_scores if response else None, 'Protecting Your Family')
            financial_knowledge_score = get_category_score(response.category_scores if response else None, 'Emergency Savings')
            
            writer.writerow([
                # Consultation Request Data
                request.id,
                request.status,
                request.source,
                request.preferred_contact_method,
                request.preferred_time or '',
                request.message or '',
                request.created_at.strftime('%Y-%m-%d %H:%M:%S') if request.created_at else '',
                request.contacted_at.strftime('%Y-%m-%d %H:%M:%S') if request.contacted_at else '',
                request.scheduled_at.strftime('%Y-%m-%d %H:%M:%S') if request.scheduled_at else '',
                request.notes or '',
                
                # Profile Data
                profile.id if profile else '',
                profile.name if profile else request.name,
                profile.email if profile else request.email,
                profile.mobile_number if profile else request.phone_number,
                profile.date_of_birth if profile else '',
                calculate_age(profile.date_of_birth) if profile and profile.date_of_birth else '',
                profile.gender if profile else '',
                profile.nationality if profile else '',
                profile.emirate if profile else '',
                profile.children if profile else '',
                profile.employment_status if profile else '',
                profile.income_range if profile else '',
                '',  # Company (from company_tracker_id if available)
                
                # Assessment Results
                response.id if response else '',
                round(response.total_score, 2) if response else '',
                response.status_band if response else '',
                response.questions_answered if response else '',
                response.total_questions if response else '',
                
                # Category Scores
                income_stream_score,
                savings_habit_score,
                debt_management_score,
                retirement_planning_score,
                financial_protection_score,
                financial_knowledge_score,
                
                # Submission Date
                response.created_at.strftime('%Y-%m-%d %H:%M:%S') if response and response.created_at else ''
            ])
        
        # Log the export
        audit_log = AuditLog(
            user_id=current_user.id,
            action="consultation_requests_exported",
            entity_type="consultation_request",
            details={
                "exported_count": len(results),
                "filters": {
                    "status": status,
                    "source": source,
                    "date_from": date_from,
                    "date_to": date_to
                },
                "admin_email": current_user.email,
                "includes_financial_clinic_data": True
            }
        )
        db.add(audit_log)
        db.commit()
        
        # Prepare response
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"consultation_leads_comprehensive_{timestamp}.csv"
        
        logger.info(f"✅ Comprehensive consultation leads exported by {current_user.email}: {len(results)} records")
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        logger.error(f"❌ Error exporting consultation requests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export consultation requests: {str(e)}"
        )


@router.get("/admin/sources")
async def get_consultation_sources(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get list of consultation request sources."""
    try:
        # Get unique sources from database
        sources = db.query(ConsultationRequest.source).distinct().all()
        source_list = [source[0] for source in sources if source[0]]
        
        # Add default sources if not present
        default_sources = ["financial_clinic", "website", "social_media", "referral"]
        for source in default_sources:
            if source not in source_list:
                source_list.append(source)
        
        return {"sources": sorted(source_list)}
        
    except Exception as e:
        logger.error(f"❌ Error getting consultation sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consultation sources"
        )


# Scheduled Email Endpoints
@router.post("/admin/schedule-email")
async def schedule_leads_email(
    request_body: dict = Body(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Schedule an email with CSV export of consultation leads."""
    from app.consultations.scheduled_email_service import ScheduledEmailService
    from dateutil import parser
    
    try:
        # Extract fields from request body
        recipient_emails = request_body.get('recipient_emails', [])
        scheduled_datetime_str = request_body.get('scheduled_datetime')
        subject = request_body.get('subject')
        status_filter = request_body.get('status_filter')
        source_filter = request_body.get('source_filter')
        date_from_str = request_body.get('date_from')
        date_to_str = request_body.get('date_to')
        
        # Validate required fields
        if not recipient_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one recipient email is required"
            )
        
        if not scheduled_datetime_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled datetime is required"
            )
        
        # Parse the datetime string
        scheduled_dt = parser.isoparse(scheduled_datetime_str)
        
        # Validate scheduled datetime is in the future
        # Use timezone-aware datetime for comparison
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        if scheduled_dt <= now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled datetime must be in the future"
            )
        
        # Parse optional dates
        date_from_dt = parser.isoparse(date_from_str) if date_from_str else None
        date_to_dt = parser.isoparse(date_to_str) if date_to_str else None
        
        # Create scheduled email
        service = ScheduledEmailService()
        scheduled_email = await service.schedule_leads_export(
            db=db,
            recipient_emails=recipient_emails,
            scheduled_datetime=scheduled_dt,
            created_by_id=current_user.id,
            subject=subject,
            status_filter=status_filter,
            source_filter=source_filter,
            date_from=date_from_dt,
            date_to=date_to_dt
        )
        
        # Log the action
        audit_log = AuditLog(
            user_id=current_user.id,
            action="scheduled_email_created",
            entity_type="scheduled_email",
            entity_id=scheduled_email.id,
            details={
                "recipient_count": len(recipient_emails),
                "scheduled_datetime": scheduled_dt.isoformat(),
                "admin_email": current_user.email
            }
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"✅ Scheduled email created by {current_user.email}: ID {scheduled_email.id}")
        
        return {
            "success": True,
            "message": "Email scheduled successfully",
            "scheduled_email": {
                "id": scheduled_email.id,
                "recipient_emails": scheduled_email.recipient_emails,
                "subject": scheduled_email.subject,
                "scheduled_datetime": scheduled_email.scheduled_datetime.isoformat(),
                "status": scheduled_email.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error scheduling email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule email: {str(e)}"
        )


@router.get("/admin/scheduled-emails")
async def list_scheduled_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all scheduled emails."""
    from app.consultations.scheduled_email_service import ScheduledEmailService
    from app.models import ScheduledEmail
    
    try:
        service = ScheduledEmailService()
        scheduled_emails = await service.get_scheduled_emails(db, skip=skip, limit=limit)
        
        return {
            "scheduled_emails": [
                {
                    "id": email.id,
                    "recipient_emails": email.recipient_emails,
                    "subject": email.subject,
                    "scheduled_datetime": email.scheduled_datetime.isoformat(),
                    "status": email.status,
                    "error_message": email.error_message,
                    "created_at": email.created_at.isoformat(),
                    "sent_at": email.sent_at.isoformat() if email.sent_at else None
                }
                for email in scheduled_emails
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing scheduled emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scheduled emails"
        )


@router.delete("/admin/scheduled-emails/{email_id}")
async def cancel_scheduled_email(
    email_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Cancel a scheduled email."""
    from app.consultations.scheduled_email_service import ScheduledEmailService
    
    try:
        service = ScheduledEmailService()
        result = await service.cancel_scheduled_email(db, email_id)
        
        if result['success']:
            # Log the cancellation
            audit_log = AuditLog(
                user_id=current_user.id,
                action="scheduled_email_cancelled",
                entity_type="scheduled_email",
                entity_id=email_id,
                details={
                    "admin_email": current_user.email
                }
            )
            db.add(audit_log)
            db.commit()
            
            logger.info(f"✅ Scheduled email {email_id} cancelled by {current_user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error cancelling scheduled email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scheduled email: {str(e)}"
        )

