import logging
from datetime import datetime, timedelta, timezone
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.email_automation_model import EmailAutomationConfig, UnsubscribedUser
from app.models import IncompleteSurvey, FinancialClinicResponse, FinancialClinicProfile, CompanyTracker
from app.reports.email_service import EmailReportService
from app.config import settings

logger = logging.getLogger(__name__)

MAX_REMINDERS = 2  # Maximum automated reminder emails per user per campaign


async def check_and_send_reminders():
    """
    Check for users who need reminders and send them emails.
    This function is scheduled to run periodically.
    """
    logger.info("🔄 Starting email reminder check...")
    
    db = SessionLocal()
    try:
        # Get configuration
        config = db.query(EmailAutomationConfig).first()
        if not config:
            logger.info("ℹ️ No email automation config found. Skipping.")
            return

        # Build unsubscribed set once for efficiency
        unsubscribed_emails = {
            row.email.lower()
            for row in db.query(UnsubscribedUser.email).all()
        }

        # Build allowed (whitelist) set; empty means "send to all"
        allowed_emails = None
        if config.allowed_emails:
            allowed_emails = {e.strip().lower() for e in config.allowed_emails if e.strip()}

        email_service = EmailReportService()
        
        # --- 1. Incomplete Survey Reminders ---
        if config.incomplete_enabled:
            await _process_incomplete_reminders(db, config, email_service, unsubscribed_emails, allowed_emails)
        else:
            logger.info("ℹ️ Incomplete survey reminders are disabled.")
            
        # --- 2. 6-Month Checkup Reminders ---
        if config.checkup_enabled:
            await _process_checkup_reminders(db, config, email_service, unsubscribed_emails, allowed_emails)
        else:
            logger.info("ℹ️ Checkup reminders are disabled.")
            
    except Exception as e:
        logger.error(f"❌ Error in email reminder check: {e}")
    finally:
        db.close()
        logger.info("✅ Email reminder check completed.")


def run_check_and_send_reminders():
    """Synchronous wrapper for check_and_send_reminders for APScheduler."""
    import asyncio
    asyncio.run(check_and_send_reminders())


def _is_email_allowed(email: str, unsubscribed: set, whitelist) -> bool:
    """Check if an email should receive automated emails."""
    email_lower = email.lower()
    if email_lower in unsubscribed:
        logger.info(f"⏭️ Skipping {email} — unsubscribed.")
        return False
    if whitelist is not None and email_lower not in whitelist:
        logger.info(f"⏭️ Skipping {email} — not in allowed list.")
        return False
    return True


async def _process_incomplete_reminders(
    db: Session,
    config: EmailAutomationConfig,
    email_service: EmailReportService,
    unsubscribed_emails: set,
    allowed_emails
):
    """Process reminders for incomplete surveys."""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=float(config.incomplete_days))
        
        # Only target surveys that still have reminders left (< MAX_REMINDERS)
        incomplete_surveys = db.query(IncompleteSurvey).filter(
            IncompleteSurvey.follow_up_count < MAX_REMINDERS,
            IncompleteSurvey.last_activity < cutoff_date,
            IncompleteSurvey.email.isnot(None)
        ).limit(settings.EMAIL_BATCH_SIZE).all()
        
        logger.info(f"📋 Found {len(incomplete_surveys)} incomplete surveys to remind (Batch Size: {settings.EMAIL_BATCH_SIZE}).")
        
        for i, survey in enumerate(incomplete_surveys):
            if not _is_email_allowed(survey.email, unsubscribed_emails, allowed_emails):
                continue
            
            # Throttle emails
            if i > 0:
                time.sleep(settings.EMAIL_THROTTLE_DELAY)
                
            try:
                # Generate resume link
                frontend_url = settings.base_url.rstrip('/')
                resume_link = f"{frontend_url}/financial-clinic?session={survey.session_id}"
                if survey.company_url:
                    resume_link = f"{frontend_url}/company/{survey.company_url}/financial-clinic?session={survey.session_id}"
                
                # Extract customer name + language from saved responses
                customer_name = "Valued Customer"
                language = "en"
                
                if survey.responses and isinstance(survey.responses, dict):
                    if 'name' in survey.responses:
                        customer_name = survey.responses['name']
                    elif survey.email:
                        customer_name = survey.email.split('@')[0]
                    if 'language' in survey.responses:
                        language = survey.responses['language']
                
                result = await email_service.send_reminder_email(
                    recipient_email=survey.email,
                    customer_name=customer_name,
                    language=language,
                    resume_link=resume_link,
                    subject_template=config.incomplete_subject_ar if language == 'ar' else config.incomplete_subject_en,
                    body_template=config.incomplete_body_ar if language == 'ar' else config.incomplete_body_en
                )
                
                if result.get('success'):
                    survey.follow_up_sent = True
                    survey.follow_up_count = (survey.follow_up_count or 0) + 1
                    
                    if not survey.is_abandoned:
                        survey.is_abandoned = True
                        survey.abandoned_at = datetime.now(timezone.utc)
                        
                    logger.info(f"✅ Sent incomplete reminder #{survey.follow_up_count} to {survey.email}")
                else:
                    logger.warning(f"⚠️ Failed to send incomplete reminder to {survey.email}: {result.get('message')}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing incomplete survey {survey.id}: {e}")
                
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error in _process_incomplete_reminders: {e}")


async def _process_checkup_reminders(
    db: Session,
    config: EmailAutomationConfig,
    email_service: EmailReportService,
    unsubscribed_emails: set,
    allowed_emails
):
    """Process 6-month checkup reminders."""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=float(config.checkup_days))
        
        # Find profiles with a response older than cutoff
        # AND still have reminders left (< MAX_REMINDERS)
        # AND (last_reminder_at IS NULL OR last_reminder_at < cutoff_date)
        candidates = db.query(FinancialClinicProfile).join(FinancialClinicResponse).filter(
            FinancialClinicResponse.completed_at < cutoff_date,
            FinancialClinicProfile.reminder_sent_count < MAX_REMINDERS,
            (FinancialClinicProfile.last_reminder_at == None) | (FinancialClinicProfile.last_reminder_at < cutoff_date)
        ).distinct().limit(settings.EMAIL_BATCH_SIZE).all()
        
        logger.info(f"📋 Found {len(candidates)} candidates for checkup reminder (Batch Size: {settings.EMAIL_BATCH_SIZE}).")
        
        count = 0
        for i, profile in enumerate(candidates):
            if not _is_email_allowed(profile.email, unsubscribed_emails, allowed_emails):
                continue

            # Throttle emails
            if i > 0:
                time.sleep(settings.EMAIL_THROTTLE_DELAY)

            # Double check: does this user have a NEWER survey?
            latest_response = db.query(FinancialClinicResponse).filter(
                FinancialClinicResponse.profile_id == profile.id
            ).order_by(FinancialClinicResponse.completed_at.desc()).first()
            
            if latest_response and latest_response.completed_at >= cutoff_date:
                # User has completed a survey recently, no need to remind
                continue
                
            try:
                # --- Language detection from latest response ---
                language = "en"
                if latest_response and latest_response.answers and isinstance(latest_response.answers, dict):
                    language = latest_response.answers.get('language', 'en')
                
                result = await email_service.send_checkup_reminder(
                    recipient_email=profile.email,
                    customer_name=profile.name,
                    language=language,
                    subject_template=config.checkup_subject_ar if language == 'ar' else config.checkup_subject_en,
                    body_template=config.checkup_body_ar if language == 'ar' else config.checkup_body_en
                )
                
                if result.get('success'):
                    profile.reminder_sent_count = (profile.reminder_sent_count or 0) + 1
                    profile.last_reminder_at = datetime.now(timezone.utc)
                    count += 1
                    logger.info(f"✅ Sent checkup reminder #{profile.reminder_sent_count} to {profile.email}")
                else:
                    logger.warning(f"⚠️ Failed to send checkup reminder to {profile.email}: {result.get('message')}")
            
            except Exception as e:
                logger.error(f"❌ Error processing checkup reminder for profile {profile.id}: {e}")
        
        db.commit()
        logger.info(f"✅ Sent {count} checkup reminders.")

    except Exception as e:
        logger.error(f"❌ Error in _process_checkup_reminders: {e}")
