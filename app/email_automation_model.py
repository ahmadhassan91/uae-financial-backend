from sqlalchemy import Column, Integer, Boolean, DateTime
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
    incomplete_days = Column(Integer, default=2, nullable=False)  # Days after inactivity
    
    # 6-Month Checkup Reminders
    checkup_enabled = Column(Boolean, default=False, nullable=False)
    checkup_days = Column(Integer, default=180, nullable=False)  # Days after completion
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
