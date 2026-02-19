import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.email_automation_model import EmailAutomationConfig
from app.models import IncompleteSurvey, FinancialClinicResponse, FinancialClinicProfile, CompanyTracker
from app.reports.email_service import EmailReportService
from app.config import settings

logger = logging.getLogger(__name__)

async def check_and_send_reminders():
    """
    Check for users who need reminders and send them emails.
    This function is scheduled to run periodically (e.g., daily).
    """
    logger.info("🔄 Starting email reminder check...")
    
    db = SessionLocal()
    try:
        # Get configuration
        config = db.query(EmailAutomationConfig).first()
        if not config:
            logger.info("ℹ️ No email automation config found. Skipping.")
            return

        email_service = EmailReportService()
        
        # --- 1. Incomplete Survey Reminders ---
        if config.incomplete_enabled:
            await _process_incomplete_reminders(db, config, email_service)
        else:
            logger.info("ℹ️ Incomplete survey reminders are disabled.")
            
        # --- 2. 6-Month Checkup Reminders ---
        if config.checkup_enabled:
            await _process_checkup_reminders(db, config, email_service)
        else:
            logger.info("ℹ️ Checkup reminders are disabled.")
            
    except Exception as e:
        logger.error(f"❌ Error in email reminder check: {e}")
    finally:
        db.close()
        logger.info("✅ Email reminder check completed.")


async def _process_incomplete_reminders(db: Session, config: EmailAutomationConfig, email_service: EmailReportService):
    """Process reminders for incomplete surveys."""
    try:
        # Rules:
        # - Abandoned (is_abandoned = True)
        # - Updated more than X days ago (last_activity < now - incomplete_days)
        # - Not yet sent follow-up (follow_up_sent = False)
        # - Has email address
        
        cutoff_date = datetime.utcnow() - timedelta(days=config.incomplete_days)
        
        incomplete_surveys = db.query(IncompleteSurvey).filter(
            IncompleteSurvey.is_abandoned == True,
            IncompleteSurvey.follow_up_sent == False,
            IncompleteSurvey.last_activity < cutoff_date,
            IncompleteSurvey.email.isnot(None)
        ).all()
        
        logger.info(f"📋 Found {len(incomplete_surveys)} incomplete surveys to remind.")
        
        for survey in incomplete_surveys:
            try:
                # Generate resume link
                frontend_url = settings.base_url.rstrip('/')
                resume_link = f"{frontend_url}/financial-clinic?session={survey.session_id}"
                if survey.company_url:
                    resume_link = f"{frontend_url}/company/{survey.company_url}/financial-clinic?session={survey.session_id}"
                
                # Extract customer name details
                customer_name = "Valued Customer"
                language = "en"
                
                # Try to get details from responses
                if survey.responses and isinstance(survey.responses, dict):
                    if 'name' in survey.responses:
                        customer_name = survey.responses['name']
                    elif survey.email:
                         customer_name = survey.email.split('@')[0]
                         
                    if 'language' in survey.responses:
                        language = survey.responses['language']
                
                # Send email
                result = await email_service.send_reminder_email(
                    recipient_email=survey.email,
                    customer_name=customer_name,
                    language=language,
                    resume_link=resume_link
                )
                
                if result.get('success'):
                    survey.follow_up_sent = True
                    survey.follow_up_count += 1
                    logger.info(f"✅ Sent incomplete reminder to {survey.email}")
                else:
                    logger.warning(f"⚠️ Failed to send incomplete reminder to {survey.email}: {result.get('message')}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing incomplete survey {survey.id}: {e}")
                
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error in _process_incomplete_reminders: {e}")


async def _process_checkup_reminders(db: Session, config: EmailAutomationConfig, email_service: EmailReportService):
    """Process 6-month checkup reminders."""
    try:
        # Rules:
        # - Has a completed survey older than X days (completed_at < now - checkup_days)
        # - Has NOT received a reminder recently (last_reminder_at is null OR old)
        # - Has NOT completed another survey since then (no newer response)
        
        cutoff_date = datetime.utcnow() - timedelta(days=config.checkup_days)
        
        # Subquery to find latest completion date per profile
        # This is complex, so we'll fetch candidate profiles first
        
        # Find profiles with a response older than cutoff
        # AND (last_reminder_at IS NULL OR last_reminder_at < cutoff - 30 days buffer?) 
        # Actually, let's just say we remind once per cycle. 
        # Let's say we remind if last_reminder_at is NULL or < cutoff_date (meaning previous cycle).
        
        candidates = db.query(FinancialClinicProfile).join(FinancialClinicResponse).filter(
            FinancialClinicResponse.completed_at < cutoff_date,
            (FinancialClinicProfile.last_reminder_at == None) | (FinancialClinicProfile.last_reminder_at < cutoff_date)
        ).distinct().all()
        
        logger.info(f"📋 Found {len(candidates)} candidates for checkup reminder.")
        
        count = 0
        for profile in candidates:
            # Double check: does this user have a NEWER survey?
            latest_response = db.query(FinancialClinicResponse).filter(
                FinancialClinicResponse.profile_id == profile.id
            ).order_by(FinancialClinicResponse.completed_at.desc()).first()
            
            if latest_response and latest_response.completed_at >= cutoff_date:
                # User has completed a survey recently, no need to remind
                continue
                
            try:
                # Send reminder
                # Determine language from latest response or profile default
                language = "en" 
                # Ideally language should be stored on profile or response. 
                # Assuming 'en' default for now as profile doesn't strictly have language preference column yet, 
                # but we can check if we can derive it.
                # Let's check latest response insights or something? 
                # For now default to 'en'.
                
                result = await email_service.send_checkup_reminder(
                    recipient_email=profile.email,
                    customer_name=profile.name,
                    language=language
                )
                
                if result.get('success'):
                    profile.reminder_sent_count += 1
                    profile.last_reminder_at = datetime.utcnow()
                    count += 1
                    logger.info(f"✅ Sent checkup reminder to {profile.email}")
                else:
                    logger.warning(f"⚠️ Failed to send checkup reminder to {profile.email}: {result.get('message')}")
            
            except Exception as e:
                logger.error(f"❌ Error processing checkup reminder for profile {profile.id}: {e}")
        
        db.commit()
        logger.info(f"✅ Sent {count} checkup reminders.")

    except Exception as e:
        logger.error(f"❌ Error in _process_checkup_reminders: {e}")
