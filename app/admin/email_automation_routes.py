from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.email_automation_model import EmailAutomationConfig, UnsubscribedUser
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# --- Schemas ---

class EmailConfigResponse(BaseModel):
    id: int
    incomplete_enabled: bool
    incomplete_days: float
    checkup_enabled: bool
    checkup_days: float
    
    incomplete_subject_en: Optional[str] = None
    incomplete_subject_ar: Optional[str] = None
    incomplete_body_en: Optional[str] = None
    incomplete_body_ar: Optional[str] = None
    
    checkup_subject_en: Optional[str] = None
    checkup_subject_ar: Optional[str] = None
    checkup_body_en: Optional[str] = None
    checkup_body_ar: Optional[str] = None
    
    allowed_emails: Optional[List[str]] = None
    incomplete_exclude_company_url: bool = False
    checkup_exclude_company_url: bool = False
    
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EmailConfigUpdate(BaseModel):
    incomplete_enabled: bool
    incomplete_days: float
    checkup_enabled: bool
    checkup_days: float
    
    incomplete_subject_en: Optional[str] = None
    incomplete_subject_ar: Optional[str] = None
    incomplete_body_en: Optional[str] = None
    incomplete_body_ar: Optional[str] = None
    
    checkup_subject_en: Optional[str] = None
    checkup_subject_ar: Optional[str] = None
    checkup_body_en: Optional[str] = None
    checkup_body_ar: Optional[str] = None
    
    allowed_emails: Optional[List[str]] = None  # Whitelist; empty/null = send to all
    incomplete_exclude_company_url: bool = False
    checkup_exclude_company_url: bool = False


class UnsubscribeRequest(BaseModel):
    email: str
    reason: Optional[str] = None


class UnsubscribedEmailResponse(BaseModel):
    id: int
    email: str
    unsubscribed_at: datetime

    class Config:
        from_attributes = True


# --- Admin Endpoints ---

DEFAULT_INCOMPLETE_SUBJECT_EN = "You've opened the door. Now step inside."
DEFAULT_INCOMPLETE_SUBJECT_AR = "لقد فتحتم الباب، وحان وقت الخطوة الأولى."
DEFAULT_INCOMPLETE_BODY_EN = (
    "Hi {customer_name},\n\n"
    "You've already started your journey toward financial clarity.\n\n"
    "The good news? You're just a few steps away from gaining complete financial clarity.\n\n"
    "Take this quick test to see exactly where you stand financially and learn about it in the most simple and practical way.\n\n"
    "Don't stop halfway. The clarity you're looking for is just moments away.\n\n"
    "Complete your financial check-up now:\n{resume_link}"
)
DEFAULT_INCOMPLETE_BODY_AR = (
    "مرحبًا {customer_name}،\n\n"
    "لقد بدأتم بالفعل رحلتكم نحو معرفة وضعكم المالي.\n\n"
    "والخبر السار هو! أنكم على بُعد خطوات قليلة من التعرف على صحتكم المالية.\n\n"
    "في دقائق معدودة، ستحصلون على تقرير واضح بطريقة بسيطة وعملية وسهلة.\n\n"
    "لا تتوقفوا في منتصف الطريق، فالوضوح الذي تبحثون عنه أقرب مما تتصورون.\n\n"
    "أكملوا فحصكم المالي الآن:\n{resume_link}"
)

DEFAULT_CHECKUP_SUBJECT_EN = "Time for Your Financial Health Checkup"
DEFAULT_CHECKUP_SUBJECT_AR = "حان وقت مراجعة صحتك المالية"
DEFAULT_CHECKUP_BODY_EN = (
    "It's been a while since your last Financial Health Assessment.\n\n"
    "Financial health is a journey, not a destination. Regular checkups help you track your progress "
    "and adjust your strategy as your life changes.\n\n"
    "Why take a new assessment?\n"
    "- See how your score has improved\n"
    "- Update your financial goals\n"
    "- Get fresh recommendations\n\n"
    "Complete your financial check-up now:\n"
    "https://financialclinic.ae/company/nationalbonds/financial-clinic"
)
DEFAULT_CHECKUP_BODY_AR = (
    "لقد مر بعض الوقت منذ آخر تقييم لصحتك المالية.\n\n"
    "الصحة المالية هي رحلة وليست وجهة. تساعدك المراجعات المنتظمة على تتبع تقدمك وتعديل استراتيجيتك مع تغير حياتك.\n\n"
    "لماذا تجري تقييماً جديداً؟\n"
    "- شاهد كيف تحسنت نتيجتك\n"
    "- قم بتحديث أهدافك المالية\n"
    "- احصل على توصيات جديدة\n\n"
    "أكملوا فحصكم المالي الآن:\n"
    "https://financialclinic.ae/company/nationalbonds/financial-clinic"
)


@router.get("/email-config", response_model=EmailConfigResponse)
def get_email_config(db: Session = Depends(get_db)):
    """Get the current email automation configuration. Creates a default if none exists."""
    config = db.query(EmailAutomationConfig).first()
    if not config:
        config = EmailAutomationConfig()
        db.add(config)
        db.commit()
        db.refresh(config)

    # Apply defaults for any fields that are missing, blank, or too short to be real content
    def _needs_default(val, min_len=20):
        return not val or len(val.strip()) < min_len

    if _needs_default(config.incomplete_subject_en, 10):
        config.incomplete_subject_en = DEFAULT_INCOMPLETE_SUBJECT_EN
    if _needs_default(config.incomplete_subject_ar, 10):
        config.incomplete_subject_ar = DEFAULT_INCOMPLETE_SUBJECT_AR
    if _needs_default(config.incomplete_body_en):
        config.incomplete_body_en = DEFAULT_INCOMPLETE_BODY_EN
    if _needs_default(config.incomplete_body_ar):
        config.incomplete_body_ar = DEFAULT_INCOMPLETE_BODY_AR

    if _needs_default(config.checkup_subject_en, 10):
        config.checkup_subject_en = DEFAULT_CHECKUP_SUBJECT_EN
    if _needs_default(config.checkup_subject_ar, 10):
        config.checkup_subject_ar = DEFAULT_CHECKUP_SUBJECT_AR
    if _needs_default(config.checkup_body_en):
        config.checkup_body_en = DEFAULT_CHECKUP_BODY_EN
    if _needs_default(config.checkup_body_ar):
        config.checkup_body_ar = DEFAULT_CHECKUP_BODY_AR

    return config

@router.put("/email-config", response_model=EmailConfigResponse)
def update_email_config(config_in: EmailConfigUpdate, db: Session = Depends(get_db)):
    """Update the email automation configuration."""
    config = db.query(EmailAutomationConfig).first()
    if not config:
        config = EmailAutomationConfig()
        db.add(config)
    
    config.incomplete_enabled = config_in.incomplete_enabled
    config.incomplete_days = config_in.incomplete_days
    config.checkup_enabled = config_in.checkup_enabled
    config.checkup_days = config_in.checkup_days
    
    config.incomplete_subject_en = config_in.incomplete_subject_en
    config.incomplete_subject_ar = config_in.incomplete_subject_ar
    config.incomplete_body_en = config_in.incomplete_body_en
    config.incomplete_body_ar = config_in.incomplete_body_ar
    
    config.checkup_subject_en = config_in.checkup_subject_en
    config.checkup_subject_ar = config_in.checkup_subject_ar
    config.checkup_body_en = config_in.checkup_body_en
    config.checkup_body_ar = config_in.checkup_body_ar
    
    # Normalise whitelist: strip and lower case
    if config_in.allowed_emails is not None:
        cleaned = [e.strip().lower() for e in config_in.allowed_emails if e.strip()]
        config.allowed_emails = cleaned if cleaned else None
    else:
        config.allowed_emails = None

    config.incomplete_exclude_company_url = config_in.incomplete_exclude_company_url
    config.checkup_exclude_company_url = config_in.checkup_exclude_company_url
    
    db.commit()
    db.refresh(config)
    return config


# --- Unsubscribe Endpoints (public — no auth required) ---

@router.post("/unsubscribe")
def unsubscribe_email(request: UnsubscribeRequest, db: Session = Depends(get_db)):
    """Unsubscribe an email from automated reminder emails."""
    email = request.email.strip().lower()
    existing = db.query(UnsubscribedUser).filter(UnsubscribedUser.email == email).first()
    if existing:
        return {"success": True, "message": f"{email} is already unsubscribed."}
    
    entry = UnsubscribedUser(email=email, reason=request.reason)
    db.add(entry)
    db.commit()
    return {"success": True, "message": f"{email} has been unsubscribed from automated emails."}


@router.get("/unsubscribe")
def unsubscribe_email_get(email: str, db: Session = Depends(get_db)):
    """Unsubscribe an email via GET request (for email link clicks)."""
    email = email.strip().lower()
    existing = db.query(UnsubscribedUser).filter(UnsubscribedUser.email == email).first()
    if existing:
        return {"success": True, "message": f"{email} is already unsubscribed."}
    
    entry = UnsubscribedUser(email=email)
    db.add(entry)
    db.commit()
    return {"success": True, "message": f"{email} has been unsubscribed from automated emails."}


@router.get("/unsubscribed-list", response_model=List[UnsubscribedEmailResponse])
def get_unsubscribed_list(db: Session = Depends(get_db)):
    """Get all unsubscribed email addresses (admin view)."""
    return db.query(UnsubscribedUser).order_by(UnsubscribedUser.unsubscribed_at.desc()).all()


@router.delete("/unsubscribe/{email}")
def resubscribe_email(email: str, db: Session = Depends(get_db)):
    """Re-add an email to the mailing list (remove from unsubscribed list)."""
    email = email.strip().lower()
    entry = db.query(UnsubscribedUser).filter(UnsubscribedUser.email == email).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Email not found in unsubscribed list.")
    db.delete(entry)
    db.commit()
    return {"success": True, "message": f"{email} has been re-subscribed."}


# --- Test / Debug Endpoints ---

class TestEmailRequest(BaseModel):
    email: str
    name: str = "Test User"
    language: str = "en"  # "en" or "ar"
    resume_link: Optional[str] = "https://financialclinic.ae/company/nationalbonds/financial-clinic"


@router.post("/test-reminder-email")
async def test_reminder_email(request: TestEmailRequest):
    """
    Manually trigger a test INCOMPLETE survey reminder email.
    Useful for verifying the template looks correct before going live.
    """
    from app.reports.email_service import EmailReportService
    service = EmailReportService()
    result = await service.send_reminder_email(
        recipient_email=request.email,
        customer_name=request.name,
        language=request.language,
        resume_link=request.resume_link,
    )
    return result


@router.post("/test-checkup-email")
async def test_checkup_email(request: TestEmailRequest):
    """
    Manually trigger a test PERIODIC CHECKUP reminder email.
    Useful for verifying the template looks correct before going live.
    """
    from app.reports.email_service import EmailReportService
    service = EmailReportService()
    result = await service.send_checkup_reminder(
        recipient_email=request.email,
        customer_name=request.name,
        language=request.language,
    )
    return result
