from sqlalchemy import Column, Integer, Boolean, DateTime, Float, String, Text
from sqlalchemy.sql import func
from app.database import Base

class EmailAutomationConfig(Base):
    """
    Configuration for automated email reminders.
    Singleton-like table (usually only 1 row) to control system-wide settings.
    """
    __tablename__ = "email_automation_config"

    id = Column(Integer, primary_key=True, index=True)
    
    # Incomplete Survey Reminders
    incomplete_enabled = Column(Boolean, default=False, nullable=False)
    incomplete_days = Column(Float, default=2.0, nullable=False)  # Float for fractional days
    
    incomplete_subject_en = Column(String, nullable=True)
    incomplete_subject_ar = Column(String, nullable=True)
    incomplete_body_en = Column(Text, nullable=True)
    incomplete_body_ar = Column(Text, nullable=True)
    
    # 6-Month Checkup Reminders
    checkup_enabled = Column(Boolean, default=False, nullable=False)
    checkup_days = Column(Float, default=180.0, nullable=False)  # Float for fractional days

    checkup_subject_en = Column(String, nullable=True)
    checkup_subject_ar = Column(String, nullable=True)
    checkup_body_en = Column(Text, nullable=True)
    checkup_body_ar = Column(Text, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
