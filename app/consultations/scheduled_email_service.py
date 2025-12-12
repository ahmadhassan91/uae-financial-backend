"""Service for scheduling and sending consultation leads via email."""
import logging
import io
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models import (
    ScheduledEmail, ConsultationRequest, FinancialClinicProfile, 
    FinancialClinicResponse, User
)
from app.scheduler_setup import get_scheduler
from app.reports.email_service import EmailReportService

logger = logging.getLogger(__name__)


class ScheduledEmailService:
    """Service for managing scheduled email exports of consultation leads."""
    
    def __init__(self):
        self.email_service = EmailReportService()
    
    async def schedule_leads_export(
        self,
        db: Session,
        recipient_emails: List[str],
        scheduled_datetime: datetime,
        created_by_id: int,
        subject: Optional[str] = None,
        status_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> ScheduledEmail:
        """
        Schedule a CSV export of consultation leads to be emailed at a specific time.
        
        Args:
            db: Database session
            recipient_emails: List of recipient email addresses
            scheduled_datetime: When to send the email
            created_by_id: ID of the admin user creating this schedule
            subject: Email subject (optional)
            status_filter: Filter by lead status
            source_filter: Filter by lead source
            date_from: Filter leads created after this date
            date_to: Filter leads created before this date
            
        Returns:
            ScheduledEmail object
        """
        try:
            # Generate unique job ID
            job_id = f"scheduled_email_{datetime.utcnow().timestamp()}"
            
            # Default subject
            if not subject:
                subject = f"Consultation Leads Export - {datetime.utcnow().strftime('%Y-%m-%d')}"
            
            # Create scheduled email record
            scheduled_email = ScheduledEmail(
                recipient_emails=recipient_emails,
                subject=subject,
                scheduled_datetime=scheduled_datetime,
                status_filter=status_filter,
                source_filter=source_filter,
                date_from=date_from,
                date_to=date_to,
                job_id=job_id,
                status="pending",
                created_by=created_by_id
            )
            
            db.add(scheduled_email)
            db.commit()
            db.refresh(scheduled_email)
            
            # Schedule the job with APScheduler
            scheduler = get_scheduler()
            scheduler.add_job(
                func=self._send_scheduled_leads_email,
                trigger='date',
                run_date=scheduled_datetime,
                args=[scheduled_email.id],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=300  # 5 minutes grace time
            )
            
            logger.info(f"✅ Scheduled email job created: ID {scheduled_email.id}, Job ID {job_id}")
            
            return scheduled_email
            
        except Exception as e:
            logger.error(f"❌ Error scheduling email: {str(e)}")
            db.rollback()
            raise
    
    def _send_scheduled_leads_email(self, scheduled_email_id: int):
        """
        Execute the scheduled email job (called by APScheduler).
        
        Args:
            scheduled_email_id: ID of the scheduled email record
        """
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get scheduled email record
            scheduled_email = db.query(ScheduledEmail).filter(
                ScheduledEmail.id == scheduled_email_id
            ).first()
            
            if not scheduled_email:
                logger.error(f"❌ Scheduled email {scheduled_email_id} not found")
                return
            
            if scheduled_email.status == "cancelled":
                logger.info(f"⏭️ Scheduled email {scheduled_email_id} was cancelled, skipping")
                return
            
            logger.info(f"📧 Executing scheduled email job: ID {scheduled_email_id}")
            
            # Generate CSV content
            csv_content = self._generate_leads_csv(
                db=db,
                status_filter=scheduled_email.status_filter,
                source_filter=scheduled_email.source_filter,
                date_from=scheduled_email.date_from,
                date_to=scheduled_email.date_to
            )
            
            # Send email to all recipients
            self._send_csv_email(
                recipient_emails=scheduled_email.recipient_emails,
                subject=scheduled_email.subject,
                csv_content=csv_content,
                filename=f"consultation_leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            # Update status
            scheduled_email.status = "sent"
            scheduled_email.sent_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"✅ Scheduled email sent successfully: ID {scheduled_email_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending scheduled email {scheduled_email_id}: {str(e)}")
            
            # Update status with error
            if scheduled_email:
                scheduled_email.status = "failed"
                scheduled_email.error_message = str(e)
                db.commit()
        
        finally:
            db.close()
    
    def _generate_leads_csv(
        self,
        db: Session,
        status_filter: Optional[str] = None,
        source_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> bytes:
        """
        Generate CSV content for consultation leads (reuses logic from export endpoint).
        
        Returns:
            CSV content as bytes
        """
        # Get the most recent response ID for each profile
        from sqlalchemy.sql import func
        
        subquery = db.query(
            FinancialClinicResponse.profile_id,
            func.max(FinancialClinicResponse.id).label('max_response_id')
        ).group_by(FinancialClinicResponse.profile_id).subquery()
        
        # Build query with filters
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
        
        if status_filter:
            query = query.filter(ConsultationRequest.status == status_filter)
        
        if source_filter:
            query = query.filter(ConsultationRequest.source == source_filter)
        
        if date_from:
            query = query.filter(ConsultationRequest.created_at >= date_from)
        
        if date_to:
            query = query.filter(ConsultationRequest.created_at <= date_to)
        
        # Get results
        results = query.order_by(desc(ConsultationRequest.created_at)).all()
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Consultation ID', 'Consultation Status', 'Consultation Source',
            'Preferred Contact Method', 'Preferred Time', 'Message',
            'Consultation Created At', 'Contacted At', 'Scheduled At', 'Notes',
            'Profile ID', 'Name', 'Email', 'Mobile Number', 'Date of Birth', 'Age',
            'Gender', 'Nationality', 'Emirate', 'Children',
            'Employment Status', 'Income Range', 'Company',
            'Response ID', 'Total Score', 'Status Band', 'Questions Answered', 'Total Questions',
            'Income Stream Score', 'Savings Habit Score', 'Debt Management Score',
            'Retirement Planning Score', 'Financial Protection Score', 'Financial Knowledge Score',
            'Assessment Submission Date'
        ])
        
        # Helper function to calculate age
        def calculate_age(dob_str):
            if not dob_str or dob_str.strip() == '':
                return ''
            try:
                dob = datetime.strptime(dob_str.strip(), '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return age
            except:
                return ''
        
        # Helper function to get category score
        def get_category_score(category_scores, category_name):
            if not category_scores:
                return 0
            try:
                if isinstance(category_scores, dict):
                    category_data = category_scores.get(category_name, {})
                    if isinstance(category_data, dict):
                        return round(category_data.get('score', 0), 2)
                    elif isinstance(category_data, (int, float)):
                        return round(float(category_data), 2)
                return 0
            except Exception:
                return 0
        
        # Write data rows
        for request, profile, response in results:
            # Extract category scores
            income_stream_score = get_category_score(response.category_scores if response else None, 'Income Stream')
            savings_habit_score = get_category_score(response.category_scores if response else None, 'Savings Habit')
            debt_management_score = get_category_score(response.category_scores if response else None, 'Debt Management')
            retirement_planning_score = get_category_score(response.category_scores if response else None, 'Retirement Planning')
            financial_protection_score = get_category_score(response.category_scores if response else None, 'Protecting Your Family')
            financial_knowledge_score = get_category_score(response.category_scores if response else None, 'Emergency Savings')
            
            writer.writerow([
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
                '',  # Company
                response.id if response else '',
                round(response.total_score, 2) if response else '',
                response.status_band if response else '',
                response.questions_answered if response else '',
                response.total_questions if response else '',
                income_stream_score,
                savings_habit_score,
                debt_management_score,
                retirement_planning_score,
                financial_protection_score,
                financial_knowledge_score,
                response.created_at.strftime('%Y-%m-%d %H:%M:%S') if response and response.created_at else ''
            ])
        
        # Convert to bytes
        output.seek(0)
        return output.getvalue().encode('utf-8')
    
    def _send_csv_email(
        self,
        recipient_emails: List[str],
        subject: str,
        csv_content: bytes,
        filename: str
    ):
        """
        Send email with CSV attachment to multiple recipients.
        
        Args:
            recipient_emails: List of email addresses
            subject: Email subject
            csv_content: CSV file content as bytes
            filename: Name for the CSV file attachment
        """
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        from app.config import settings
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_service.from_name} <{self.email_service.from_email}>"
            msg['To'] = ", ".join(recipient_emails)
            msg['Subject'] = subject
            
            # Email body
            body = f"""
Hello,

Please find attached the consultation leads export as requested.

This export was generated on {datetime.utcnow().strftime('%Y-%m-%d at %H:%M UTC')}.

Best regards,
UAE Financial Health Team
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_content)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(self.email_service.smtp_server, self.email_service.smtp_port)
            
            # Check if authentication is required (password is set)
            smtp_password = self.email_service.smtp_password or ''
            requires_auth = bool(smtp_password.strip())
            
            if requires_auth:
                server.starttls()
                server.login(self.email_service.smtp_username, smtp_password)
            else:
                # For internal relays without auth
                server.ehlo()
            
            server.sendmail(self.email_service.from_email, recipient_emails, msg.as_string())
            server.quit()
            
            logger.info(f"✅ CSV email sent to {len(recipient_emails)} recipients")
            
        except Exception as e:
            logger.error(f"❌ Error sending CSV email: {str(e)}")
            raise
    
    async def cancel_scheduled_email(
        self,
        db: Session,
        scheduled_email_id: int
    ) -> Dict[str, Any]:
        """
        Cancel a pending scheduled email.
        
        Args:
            db: Database session
            scheduled_email_id: ID of the scheduled email to cancel
            
        Returns:
            Result dictionary
        """
        try:
            scheduled_email = db.query(ScheduledEmail).filter(
                ScheduledEmail.id == scheduled_email_id
            ).first()
            
            if not scheduled_email:
                return {
                    'success': False,
                    'message': 'Scheduled email not found'
                }
            
            if scheduled_email.status != 'pending':
                return {
                    'success': False,
                    'message': f'Cannot cancel email with status: {scheduled_email.status}'
                }
            
            # Remove from scheduler
            scheduler = get_scheduler()
            try:
                scheduler.remove_job(scheduled_email.job_id)
            except:
                pass  # Job might not exist in scheduler
            
            # Update status
            scheduled_email.status = 'cancelled'
            db.commit()
            
            logger.info(f"✅ Cancelled scheduled email: ID {scheduled_email_id}")
            
            return {
                'success': True,
                'message': 'Scheduled email cancelled successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error cancelling scheduled email: {str(e)}")
            return {
                'success': False,
                'message': f'Error cancelling email: {str(e)}'
            }
    
    async def get_scheduled_emails(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> List[ScheduledEmail]:
        """
        Get list of scheduled emails.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ScheduledEmail objects
        """
        return db.query(ScheduledEmail).order_by(
            desc(ScheduledEmail.created_at)
        ).offset(skip).limit(limit).all()
