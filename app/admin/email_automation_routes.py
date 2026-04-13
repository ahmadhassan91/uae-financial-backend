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
    "You've already started your journey toward financial clarity.<br><br>"
    "The good news? You're just a few steps away from gaining complete financial clarity.<br><br>"
    "Take this quick test to see exactly where you stand financially and learn about it in the most simple and practical way.<br><br>"
    "Don't stop halfway. The clarity you're looking for is just moments away.<br><br>"
    "Complete your financial check-up now:"
)
DEFAULT_INCOMPLETE_BODY_AR = (
    "لقد بدأتم بالفعل رحلتكم نحو معرفة وضعكم المالي.<br><br>"
    "والخبر السار هو! أنكم على بُعد خطوات قليلة من التعرف على صحتكم المالية.<br><br>"
    "في دقائق معدودة، ستحصلون على تقرير واضح بطريقة بسيطة وعملية وسهلة.<br><br>"
    "لا تتوقفوا في منتصف الطريق، فالوضوح الذي تبحثون عنه أقرب مما تتصورون.<br><br>"
    "أكملوا فحصكم المالي الآن:"
)

DEFAULT_CHECKUP_SUBJECT_EN = "Ready for your next financial check-in?"
DEFAULT_CHECKUP_SUBJECT_AR = "هل أنتم مستعدون لفحصكم المالي التالي؟"
DEFAULT_CHECKUP_BODY_EN = (
    "It's been a while since you last checked your financial health.<br><br>"
    "Just like your physical wellbeing, your financial situation can change over time. "
    "What was right six months ago may look different today.<br><br>"
    "<strong>That's why it's a good time to revisit your Financial Clinic assessment.</strong><br><br>"
    "<strong>In just a few minutes, you can:</strong><br>"
    "&bull; Refresh your view of your current financial position<br>"
    "&bull; Identify new opportunities<br>"
    "&bull; Get updated guidance to support your next steps<br><br>"
    "<strong>The assessment is still free, quick, and comes with no obligations.</strong><br><br>"
    "Because staying on track starts with staying informed.<br><br>"
    "Take your financial check-up again:"
)
DEFAULT_CHECKUP_BODY_AR = (
    "مرّ بعض الوقت منذ آخر مرة فحصتم فيها صحتكم المالية.<br><br>"
    "وقد حان وقت فحصكم الدوري لصحتكم المالية، تمامًا مثل صحتكم الجسدية، يمكن لوضعكم المالي أن يتغير مع مرور الوقت. "
    "فما كان مناسبًا قبل ستة أشهر، قد يبدو مختلفًا اليوم.<br><br>"
    "لهذا، حان الوقت للعودة إلى تقييم العيادة المالية لصحتكم المالية الآن.<br><br>"
    "<strong>في بضع دقائق فقط، يمكنكم:</strong><br>"
    "&bull; تحديث رؤيتكم لوضعكم المالي الحالي<br>"
    "&bull; اكتشاف فرص جديدة<br>"
    "&bull; الحصول على إرشادات محدثة تدعم خطواتكم القادمة<br><br>"
    "<strong>التقييم لا يزال مجانيًا، سريعًا، ولا يترتب عليه أي التزامات.</strong><br><br>"
    "لأن البقاء على المسار الصحيح يبدأ بالاطلاع المستمر.<br><br>"
    "ابدؤوا فحصكم المالي مرة أخرى الآن:"
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
    subject: Optional[str] = None
    body: Optional[str] = None


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
        subject_template=request.subject,
        body_template=request.body
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
        subject_template=request.subject,
        body_template=request.body
    )
    return result
