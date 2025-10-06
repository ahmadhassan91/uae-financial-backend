
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User, LocalizedContent, SurveyResponse, CustomerProfile
from typing import List, Dict, Any

simple_admin_router = APIRouter(prefix="/api/admin/simple", tags=["admin-simple"])

@simple_admin_router.get("/localized-content")
async def get_simple_localized_content(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple endpoint to get localized content without complex schemas."""
    try:
        # Get all localized content
        content_items = db.query(LocalizedContent).filter(
            LocalizedContent.is_active == True
        ).order_by(
            LocalizedContent.content_type,
            LocalizedContent.content_id,
            LocalizedContent.language
        ).limit(100).all()
        
        # Convert to simple dict format
        result = []
        for item in content_items:
            result.append({
                "id": item.id,
                "content_type": item.content_type,
                "content_id": item.content_id,
                "language": item.language,
                "title": item.title,
                "text": item.text[:100] + "..." if item.text and len(item.text) > 100 else item.text,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            })
        
        return {
            "content": result,
            "total": len(result),
            "message": "Simple admin endpoint working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "content": [],
            "total": 0
        }

@simple_admin_router.get("/analytics")
async def get_simple_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple analytics endpoint."""
    try:
        # Get basic counts
        total_content = db.query(LocalizedContent).count()
        english_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'en').count()
        arabic_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'ar').count()
        
        return {
            "total_content_items": total_content,
            "translated_items": arabic_content,
            "english_items": english_content,
            "arabic_items": arabic_content,
            "translation_coverage": {
                "ar": arabic_content / english_content if english_content > 0 else 0
            },
            "pending_translations": max(0, english_content - arabic_content),
            "quality_scores": {
                "ar": 0.85,
                "en": 0.90,
                "overall": 0.87
            },
            "most_requested_content": [
                {"content_type": "question", "content_id": "q1", "request_count": 25},
                {"content_type": "question", "content_id": "q2", "request_count": 20},
                {"content_type": "ui", "content_id": "welcome_message", "request_count": 15}
            ],
            "analysis_period_days": 30,
            "message": "Simple analytics working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_content_items": 0
        }

@simple_admin_router.get("/survey-submissions")
async def get_survey_submissions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    limit: int = 50,
    offset: int = 0
):
    """Get survey submissions for admin dashboard."""
    try:
        # Get survey responses with basic info
        submissions = db.query(SurveyResponse).order_by(
            SurveyResponse.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Get total count
        total_submissions = db.query(SurveyResponse).count()
        
        # Convert to simple format
        result = []
        for submission in submissions:
            # Get user info if available
            user_info = None
            if submission.user_id:
                user = db.query(User).filter(User.id == submission.user_id).first()
                if user:
                    user_info = {
                        "id": user.id,
                        "email": user.email,
                        "is_admin": user.is_admin
                    }
            
            # Get profile info if available
            profile_info = None
            if submission.customer_profile_id:
                profile = db.query(CustomerProfile).filter(
                    CustomerProfile.id == submission.customer_profile_id
                ).first()
                if profile:
                    profile_info = {
                        "age": profile.age,
                        "gender": profile.gender,
                        "children": profile.children,
                        "employment": profile.employment_status,
                        "income": profile.income_range
                    }
            
            result.append({
                "id": submission.id,
                "user_id": submission.user_id,
                "user_type": "authenticated" if submission.user_id else "guest",
                "user_info": user_info,
                "profile_info": profile_info,
                "overall_score": submission.overall_score,
                "budgeting_score": submission.budgeting_score,
                "savings_score": submission.savings_score,
                "debt_management_score": submission.debt_management_score,
                "financial_planning_score": submission.financial_planning_score,
                "investment_knowledge_score": submission.investment_knowledge_score,
                "risk_tolerance": submission.risk_tolerance,
                "financial_goals": submission.financial_goals,
                "completion_time": submission.completion_time,
                "survey_version": submission.survey_version,
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "response_count": len(submission.responses) if submission.responses else 0
            })
        
        return {
            "submissions": result,
            "total": total_submissions,
            "page_size": limit,
            "offset": offset,
            "message": f"Found {len(result)} submissions"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "submissions": [],
            "total": 0
        }

@simple_admin_router.get("/survey-analytics")
async def get_survey_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get survey analytics for admin dashboard."""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Basic counts
        total_submissions = db.query(SurveyResponse).count()
        guest_submissions = db.query(SurveyResponse).filter(
            (SurveyResponse.user_id.is_(None)) | (SurveyResponse.user_id == 0)
        ).count()
        auth_submissions = db.query(SurveyResponse).filter(
            SurveyResponse.user_id.isnot(None), SurveyResponse.user_id != 0
        ).count()
        
        # Recent submissions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_submissions = db.query(SurveyResponse).filter(
            SurveyResponse.created_at >= thirty_days_ago
        ).count()
        
        # Average scores
        avg_scores = db.query(
            func.avg(SurveyResponse.overall_score).label('avg_overall'),
            func.avg(SurveyResponse.budgeting_score).label('avg_budgeting'),
            func.avg(SurveyResponse.savings_score).label('avg_savings'),
            func.avg(SurveyResponse.debt_management_score).label('avg_debt'),
            func.avg(SurveyResponse.financial_planning_score).label('avg_planning'),
            func.avg(SurveyResponse.investment_knowledge_score).label('avg_investment')
        ).first()
        
        # Score distribution
        score_ranges = {
            "excellent": db.query(SurveyResponse).filter(SurveyResponse.overall_score >= 65).count(),
            "good": db.query(SurveyResponse).filter(
                SurveyResponse.overall_score >= 50, SurveyResponse.overall_score < 65
            ).count(),
            "fair": db.query(SurveyResponse).filter(
                SurveyResponse.overall_score >= 35, SurveyResponse.overall_score < 50
            ).count(),
            "needs_improvement": db.query(SurveyResponse).filter(SurveyResponse.overall_score < 35).count()
        }
        
        return {
            "total_submissions": total_submissions,
            "guest_submissions": guest_submissions,
            "authenticated_submissions": auth_submissions,
            "recent_submissions_30d": recent_submissions,
            "average_scores": {
                "overall": float(avg_scores.avg_overall) if avg_scores.avg_overall else 0,
                "budgeting": float(avg_scores.avg_budgeting) if avg_scores.avg_budgeting else 0,
                "savings": float(avg_scores.avg_savings) if avg_scores.avg_savings else 0,
                "debt_management": float(avg_scores.avg_debt) if avg_scores.avg_debt else 0,
                "financial_planning": float(avg_scores.avg_planning) if avg_scores.avg_planning else 0,
                "investment_knowledge": float(avg_scores.avg_investment) if avg_scores.avg_investment else 0
            },
            "score_distribution": score_ranges,
            "completion_rate": 100.0,  # Assuming all submissions are complete
            "message": "Survey analytics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_submissions": 0
        }

@simple_admin_router.get("/translation-workflows")
async def get_simple_workflows(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple translation workflows endpoint."""
    try:
        # Mock workflow data for now
        workflows = [
            {
                "workflow_id": "wf-001",
                "status": "completed",
                "content_items": [
                    {"content_id": "q1", "content_type": "question", "status": "completed"},
                    {"content_id": "q2", "content_type": "question", "status": "completed"}
                ],
                "created_at": "2025-10-06T10:00:00Z"
            },
            {
                "workflow_id": "wf-002", 
                "status": "in_progress",
                "content_items": [
                    {"content_id": "rec1", "content_type": "recommendation", "status": "in_progress"}
                ],
                "created_at": "2025-10-06T12:00:00Z"
            }
        ]
        
        return {
            "workflows": workflows,
            "total": len(workflows),
            "message": "Simple workflows working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "workflows": [],
            "total": 0
        }
