"""API routes for report generation and delivery."""
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models import User, SurveyResponse, CustomerProfile
from .delivery_service import ReportDeliveryService


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportDeliveryRequest(BaseModel):
    """Request model for report delivery."""
    survey_response_id: int
    send_email: bool = False
    email_address: Optional[EmailStr] = None
    language: str = "en"
    branding_config: Optional[Dict[str, Any]] = None


class ResendEmailRequest(BaseModel):
    """Request model for resending report email."""
    survey_response_id: int
    email_address: EmailStr
    language: str = "en"


# Initialize the delivery service
delivery_service = ReportDeliveryService()


@router.post("/generate")
async def generate_report(
    request: ReportDeliveryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and optionally deliver a financial health report."""
    # Get the survey response
    survey_response = db.query(SurveyResponse).filter(
        SurveyResponse.id == request.survey_response_id,
        SurveyResponse.user_id == current_user.id
    ).first()
    
    if not survey_response:
        raise HTTPException(
            status_code=404,
            detail="Survey response not found"
        )
    
    # Get customer profile
    customer_profile = survey_response.customer_profile
    if not customer_profile:
        raise HTTPException(
            status_code=400,
            detail="Customer profile required for report generation"
        )
    
    # Prepare delivery options
    delivery_options = {
        'send_email': request.send_email,
        'email_address': request.email_address
    }
    
    try:
        # Generate and deliver report
        result = await delivery_service.generate_and_deliver_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            user=current_user,
            delivery_options=delivery_options,
            db=db,
            language=request.language,
            branding_config=request.branding_config
        )
        
        return {
            "success": True,
            "message": "Report generated successfully",
            "pdf_generated": result['pdf_generated'],
            "email_sent": result['email_sent'],
            "errors": result['errors']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/download/{survey_response_id}")
async def download_report(
    survey_response_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a generated PDF report."""
    # Get the file path
    file_path = await delivery_service.get_report_download_url(
        survey_response_id=survey_response_id,
        user_id=current_user.id,
        db=db
    )
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="Report not found or not available for download"
        )
    
    # Return the file
    filename = f"financial_health_report_{survey_response_id}.pdf"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )


@router.post("/resend-email")
async def resend_report_email(
    request: ResendEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend report email for an existing survey response."""
    try:
        result = await delivery_service.resend_report_email(
            survey_response_id=request.survey_response_id,
            user_id=current_user.id,
            email_address=request.email_address,
            db=db,
            language=request.language
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Report email sent successfully",
                "recipient": request.email_address
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result['message']
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resend email: {str(e)}"
        )


@router.get("/history")
async def get_delivery_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get delivery history for the current user."""
    try:
        history = await delivery_service.get_delivery_history(
            user_id=current_user.id,
            db=db,
            limit=limit
        )
        
        return {
            "success": True,
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get delivery history: {str(e)}"
        )


@router.get("/analytics/{survey_response_id}")
async def get_report_analytics(
    survey_response_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific report."""
    # Verify the survey response belongs to the current user
    survey_response = db.query(SurveyResponse).filter(
        SurveyResponse.id == survey_response_id,
        SurveyResponse.user_id == current_user.id
    ).first()
    
    if not survey_response:
        raise HTTPException(
            status_code=404,
            detail="Survey response not found"
        )
    
    try:
        analytics = await delivery_service.get_report_analytics(
            survey_response_id=survey_response_id,
            db=db
        )
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/preview/{survey_response_id}")
async def preview_report_data(
    survey_response_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview report data without generating PDF (for testing)."""
    # Get the survey response
    survey_response = db.query(SurveyResponse).filter(
        SurveyResponse.id == survey_response_id,
        SurveyResponse.user_id == current_user.id
    ).first()
    
    if not survey_response:
        raise HTTPException(
            status_code=404,
            detail="Survey response not found"
        )
    
    customer_profile = survey_response.customer_profile
    if not customer_profile:
        raise HTTPException(
            status_code=400,
            detail="Customer profile required for report preview"
        )
    
    try:
        # Get report data without generating PDF
        from app.surveys.scoring import SurveyScorer
        from app.surveys.recommendations import RecommendationEngine
        
        scorer = SurveyScorer()
        recommendation_engine = RecommendationEngine()
        
        # Recalculate scores
        responses = survey_response.responses if isinstance(survey_response.responses, dict) else {}
        profile_data = {
            'children': getattr(customer_profile, 'children', 'No')
        }
        
        detailed_scores = scorer.calculate_scores_v2(responses, profile_data)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            survey_response, customer_profile
        )
        
        return {
            "success": True,
            "survey_response": {
                "id": survey_response.id,
                "overall_score": survey_response.overall_score,
                "created_at": survey_response.created_at.isoformat()
            },
            "customer_profile": {
                "first_name": customer_profile.first_name,
                "last_name": customer_profile.last_name,
                "age": customer_profile.age,
                "nationality": customer_profile.nationality,
                "emirate": customer_profile.emirate
            },
            "detailed_scores": detailed_scores,
            "recommendations": recommendations[:5],  # Limit to top 5
            "language": language
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview report: {str(e)}"
        )


# Admin routes (if user is admin)
@router.post("/admin/cleanup")
async def cleanup_old_reports(
    days_old: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up old report files (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        result = await delivery_service.cleanup_old_reports(
            days_old=days_old,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )


@router.get("/admin/stats")
async def get_delivery_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall delivery statistics (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        from app.models import ReportDelivery
        from sqlalchemy import func
        
        # Get delivery statistics
        total_deliveries = db.query(ReportDelivery).count()
        
        email_deliveries = db.query(ReportDelivery).filter(
            ReportDelivery.delivery_type == 'email'
        ).count()
        
        pdf_downloads = db.query(ReportDelivery).filter(
            ReportDelivery.delivery_type == 'pdf_download'
        ).count()
        
        successful_emails = db.query(ReportDelivery).filter(
            ReportDelivery.delivery_type == 'email',
            ReportDelivery.delivery_status == 'sent'
        ).count()
        
        failed_emails = db.query(ReportDelivery).filter(
            ReportDelivery.delivery_type == 'email',
            ReportDelivery.delivery_status == 'failed'
        ).count()
        
        # Language distribution
        language_stats = db.query(
            ReportDelivery.language,
            func.count(ReportDelivery.id)
        ).group_by(ReportDelivery.language).all()
        
        return {
            "success": True,
            "stats": {
                "total_deliveries": total_deliveries,
                "email_deliveries": email_deliveries,
                "pdf_downloads": pdf_downloads,
                "successful_emails": successful_emails,
                "failed_emails": failed_emails,
                "email_success_rate": round(
                    (successful_emails / email_deliveries * 100) if email_deliveries > 0 else 0, 2
                ),
                "language_distribution": {
                    lang: count for lang, count in language_stats
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )