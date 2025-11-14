"""Report delivery service that coordinates PDF generation and email delivery."""
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models import (
    SurveyResponse, CustomerProfile, ReportDelivery, 
    ReportAccessLog, User
)
from app.database import get_db
from .report_generation_service import ReportGenerationService
from .email_service import EmailReportService


class ReportDeliveryService:
    """Coordinate PDF generation and email delivery for survey reports."""
    
    def __init__(self):
        """Initialize the report delivery service."""
        self.report_service = ReportGenerationService()
        self.email_service = EmailReportService()
        self.reports_dir = "reports"  # Directory to store PDF files
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_and_deliver_report(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        user: User,
        delivery_options: Dict[str, Any],
        db: Session,
        language: str = "en",
        branding_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate PDF report and deliver via requested methods."""
        results = {
            'pdf_generated': False,
            'email_sent': False,
            'pdf_path': None,
            'email_result': None,
            'errors': []
        }
        
        try:
            # Generate PDF report
            if branding_config:
                # Use company branded report
                pdf_content = await self.report_service.generate_company_branded_report(
                    survey_response=survey_response,
                    company_branding=branding_config,
                    language=language
                )
            else:
                # Use standard report
                pdf_content = await self.report_service.generate_pdf_report(
                    survey_response=survey_response,
                    language=language
                )
            
            # Save PDF to file system
            pdf_filename = f"report_{survey_response.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.reports_dir, pdf_filename)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            
            results['pdf_generated'] = True
            results['pdf_path'] = pdf_path
            
            # Create PDF delivery record
            pdf_delivery = ReportDelivery(
                survey_response_id=survey_response.id,
                user_id=user.id,
                delivery_type='pdf_download',
                delivery_status='generated',
                file_path=pdf_path,
                file_size=len(pdf_content),
                language=language,
                delivery_metadata={
                    'generation_time': datetime.now().isoformat(),
                    'branding_config': branding_config or {}
                }
            )
            db.add(pdf_delivery)
            
            # Send email if requested
            if delivery_options.get('send_email', False):
                email_address = delivery_options.get('email_address') or user.email
                
                if email_address:
                    # Generate download URL for the PDF
                    download_url = self._generate_download_url(survey_response.id, pdf_filename)
                    
                    email_result = await self.email_service.send_report_email(
                        recipient_email=email_address,
                        survey_response=survey_response,
                        customer_profile=customer_profile,
                        pdf_content=pdf_content,
                        language=language,
                        branding_config=branding_config,
                        download_url=download_url
                    )
                    
                    results['email_sent'] = email_result['success']
                    results['email_result'] = email_result
                    
                    # Create email delivery record
                    email_delivery = ReportDelivery(
                        survey_response_id=survey_response.id,
                        user_id=user.id,
                        delivery_type='email',
                        delivery_status='sent' if email_result['success'] else 'failed',
                        recipient_email=email_address,
                        file_path=pdf_path,
                        file_size=len(pdf_content),
                        language=language,
                        delivery_metadata=email_result,
                        error_message=email_result.get('error') if not email_result['success'] else None,
                        delivered_at=datetime.now() if email_result['success'] else None
                    )
                    db.add(email_delivery)
                    
                    if not email_result['success']:
                        results['errors'].append(f"Email delivery failed: {email_result.get('message', 'Unknown error')}")
                else:
                    results['errors'].append("No email address provided for email delivery")
            
            # Update survey response tracking
            survey_response.pdf_generated = True
            if results['email_sent']:
                survey_response.email_sent = True
            
            db.commit()
            
        except Exception as e:
            results['errors'].append(f"Report generation failed: {str(e)}")
            db.rollback()
        
        return results
    
    async def get_report_download_url(
        self,
        survey_response_id: int,
        user_id: int,
        db: Session
    ) -> Optional[str]:
        """Get download URL for a generated report."""
        # Find the most recent PDF delivery for this survey response
        delivery = db.query(ReportDelivery).filter(
            ReportDelivery.survey_response_id == survey_response_id,
            ReportDelivery.user_id == user_id,
            ReportDelivery.delivery_type == 'pdf_download',
            ReportDelivery.delivery_status == 'generated'
        ).order_by(ReportDelivery.created_at.desc()).first()
        
        if delivery and delivery.file_path and os.path.exists(delivery.file_path):
            # Log the access
            access_log = ReportAccessLog(
                report_delivery_id=delivery.id,
                user_id=user_id,
                access_type='download'
            )
            db.add(access_log)
            
            # Increment download counter
            delivery.survey_response.report_downloads += 1
            db.commit()
            
            return delivery.file_path
        
        return None
    
    def _generate_download_url(self, survey_response_id: int, pdf_filename: str) -> str:
        """Generate a download URL for the PDF report."""
        # Get the base URL from settings
        from app.config import settings
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Generate download URL - this will be handled by the API endpoint
        download_url = f"{base_url}/api/reports/download/{survey_response_id}"
        
        return download_url
    
    async def resend_report_email(
        self,
        survey_response_id: int,
        user_id: int,
        email_address: str,
        db: Session,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Resend report email for an existing survey response."""
        try:
            # Get the survey response and related data
            survey_response = db.query(SurveyResponse).filter(
                SurveyResponse.id == survey_response_id,
                SurveyResponse.user_id == user_id
            ).first()
            
            if not survey_response:
                return {
                    'success': False,
                    'message': 'Survey response not found'
                }
            
            customer_profile = survey_response.customer_profile
            user = survey_response.user
            
            # Find existing PDF file
            pdf_delivery = db.query(ReportDelivery).filter(
                ReportDelivery.survey_response_id == survey_response_id,
                ReportDelivery.delivery_type == 'pdf_download',
                ReportDelivery.delivery_status == 'generated'
            ).order_by(ReportDelivery.created_at.desc()).first()
            
            if not pdf_delivery or not os.path.exists(pdf_delivery.file_path):
                return {
                    'success': False,
                    'message': 'PDF report not found. Please generate a new report.'
                }
            
            # Read existing PDF content
            with open(pdf_delivery.file_path, 'rb') as f:
                pdf_content = f.read()
            
            # Send email
            email_result = await self.email_service.send_report_email(
                recipient_email=email_address,
                survey_response=survey_response,
                customer_profile=customer_profile,
                pdf_content=pdf_content,
                language=language
            )
            
            # Create new email delivery record
            email_delivery = ReportDelivery(
                survey_response_id=survey_response_id,
                user_id=user_id,
                delivery_type='email',
                delivery_status='sent' if email_result['success'] else 'failed',
                recipient_email=email_address,
                file_path=pdf_delivery.file_path,
                file_size=len(pdf_content),
                language=language,
                delivery_metadata=email_result,
                error_message=email_result.get('error') if not email_result['success'] else None,
                delivered_at=datetime.now() if email_result['success'] else None,
                retry_count=1
            )
            db.add(email_delivery)
            db.commit()
            
            return email_result
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to resend email: {str(e)}",
                'error': str(e)
            }
    
    async def get_delivery_history(
        self,
        user_id: int,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get delivery history for a user."""
        deliveries = db.query(ReportDelivery).filter(
            ReportDelivery.user_id == user_id
        ).order_by(ReportDelivery.created_at.desc()).limit(limit).all()
        
        history = []
        for delivery in deliveries:
            history.append({
                'id': delivery.id,
                'survey_response_id': delivery.survey_response_id,
                'delivery_type': delivery.delivery_type,
                'delivery_status': delivery.delivery_status,
                'recipient_email': delivery.recipient_email,
                'language': delivery.language,
                'file_size': delivery.file_size,
                'delivered_at': delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                'created_at': delivery.created_at.isoformat(),
                'error_message': delivery.error_message,
                'retry_count': delivery.retry_count
            })
        
        return history
    
    async def get_report_analytics(
        self,
        survey_response_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for a specific report."""
        # Get all deliveries for this survey response
        deliveries = db.query(ReportDelivery).filter(
            ReportDelivery.survey_response_id == survey_response_id
        ).all()
        
        # Get access logs
        access_logs = db.query(ReportAccessLog).join(ReportDelivery).filter(
            ReportDelivery.survey_response_id == survey_response_id
        ).all()
        
        analytics = {
            'total_deliveries': len(deliveries),
            'email_deliveries': len([d for d in deliveries if d.delivery_type == 'email']),
            'pdf_downloads': len([d for d in deliveries if d.delivery_type == 'pdf_download']),
            'successful_emails': len([d for d in deliveries if d.delivery_type == 'email' and d.delivery_status == 'sent']),
            'failed_emails': len([d for d in deliveries if d.delivery_type == 'email' and d.delivery_status == 'failed']),
            'total_accesses': len(access_logs),
            'download_accesses': len([a for a in access_logs if a.access_type == 'download']),
            'view_accesses': len([a for a in access_logs if a.access_type == 'view']),
            'email_opens': len([a for a in access_logs if a.access_type == 'email_open']),
            'last_access': max([a.accessed_at for a in access_logs]) if access_logs else None,
            'languages_used': list(set([d.language for d in deliveries if d.language])),
            'delivery_timeline': [
                {
                    'type': d.delivery_type,
                    'status': d.delivery_status,
                    'timestamp': d.created_at.isoformat(),
                    'delivered_at': d.delivered_at.isoformat() if d.delivered_at else None
                }
                for d in sorted(deliveries, key=lambda x: x.created_at)
            ]
        }
        
        return analytics
    
    async def cleanup_old_reports(
        self,
        days_old: int = 90,
        db: Session = None
    ) -> Dict[str, Any]:
        """Clean up old report files to save disk space."""
        if not db:
            db = next(get_db())
        
        try:
            # Find old deliveries
            cutoff_date = datetime.now() - timedelta(days=days_old)
            old_deliveries = db.query(ReportDelivery).filter(
                ReportDelivery.created_at < cutoff_date,
                ReportDelivery.delivery_type == 'pdf_download'
            ).all()
            
            cleaned_files = 0
            freed_space = 0
            errors = []
            
            for delivery in old_deliveries:
                if delivery.file_path and os.path.exists(delivery.file_path):
                    try:
                        file_size = os.path.getsize(delivery.file_path)
                        os.remove(delivery.file_path)
                        
                        # Update delivery record
                        delivery.file_path = None
                        delivery.delivery_metadata = delivery.delivery_metadata or {}
                        delivery.delivery_metadata['cleaned_up'] = datetime.now().isoformat()
                        
                        cleaned_files += 1
                        freed_space += file_size
                        
                    except Exception as e:
                        errors.append(f"Failed to delete {delivery.file_path}: {str(e)}")
            
            db.commit()
            
            return {
                'success': True,
                'cleaned_files': cleaned_files,
                'freed_space_bytes': freed_space,
                'freed_space_mb': round(freed_space / (1024 * 1024), 2),
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Cleanup failed: {str(e)}",
                'error': str(e)
            }
    
    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Get file content for download."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
        except Exception:
            pass
        return None