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

@router.get("/email-config", response_model=EmailConfigResponse)
def get_email_config(db: Session = Depends(get_db)):
    """Get the current email automation configuration. Creates a default if none exists."""
    config = db.query(EmailAutomationConfig).first()
    if not config:
        config = EmailAutomationConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
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
