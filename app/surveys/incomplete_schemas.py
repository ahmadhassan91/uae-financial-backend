"""Pydantic schemas for incomplete survey tracking."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr


class IncompleteSurveyCreate(BaseModel):
    """Schema for creating an incomplete survey session."""
    current_step: int = 0
    total_steps: int
    responses: Optional[Dict[str, Any]] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    company_url: Optional[str] = None  # For company tracking


class IncompleteSurveyUpdate(BaseModel):
    """Schema for updating an incomplete survey session."""
    current_step: Optional[int] = None
    responses: Optional[Dict[str, Any]] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    company_url: Optional[str] = None  # For company tracking


class IncompleteSurveyResponse(BaseModel):
    """Schema for incomplete survey response."""
    id: int
    session_id: str
    user_id: Optional[int]
    current_step: int
    total_steps: int
    responses: Optional[Dict[str, Any]]
    started_at: datetime
    last_activity: datetime
    abandoned_at: Optional[datetime]
    email: Optional[str]
    phone_number: Optional[str]
    company_id: Optional[int]  # For company tracking
    company_url: Optional[str]  # For company tracking
    is_abandoned: bool
    follow_up_sent: bool
    follow_up_count: int
    
    class Config:
        from_attributes = True


class IncompleteSurveyStats(BaseModel):
    """Schema for incomplete survey statistics."""
    total_incomplete: int
    abandoned_count: int
    average_completion_rate: float
    most_common_exit_step: int
    follow_up_pending: int


class FollowUpRequest(BaseModel):
    """Schema for sending follow-up communications."""
    survey_ids: List[int]
    message_template: str
    send_email: bool = True
    send_sms: bool = False