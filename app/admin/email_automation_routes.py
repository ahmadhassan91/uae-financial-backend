from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.email_automation_model import EmailAutomationConfig
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# --- Schemas ---

class EmailConfigResponse(BaseModel):
    id: int
    incomplete_enabled: bool
    incomplete_days: int
    checkup_enabled: bool
    checkup_days: int
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EmailConfigUpdate(BaseModel):
    incomplete_enabled: bool
    incomplete_days: int
    checkup_enabled: bool
    checkup_days: int

# --- Endpoints ---

@router.get("/email-config", response_model=EmailConfigResponse)
def get_email_config(db: Session = Depends(get_db)):
    """
    Get the current email automation configuration.
    Creates a default config if one doesn't exist.
    """
    config = db.query(EmailAutomationConfig).first()
    if not config:
        # Create default configuration
        config = EmailAutomationConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("/email-config", response_model=EmailConfigResponse)
def update_email_config(config_in: EmailConfigUpdate, db: Session = Depends(get_db)):
    """
    Update the email automation configuration.
    """
    config = db.query(EmailAutomationConfig).first()
    if not config:
        config = EmailAutomationConfig()
        db.add(config)
    
    # Update fields
    config.incomplete_enabled = config_in.incomplete_enabled
    config.incomplete_days = config_in.incomplete_days
    config.checkup_enabled = config_in.checkup_enabled
    config.checkup_days = config_in.checkup_days
    
    db.commit()
    db.refresh(config)
    return config
