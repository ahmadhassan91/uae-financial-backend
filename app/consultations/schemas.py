"""Pydantic schemas for consultation requests."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ConsultationRequestCreate(BaseModel):
    """Schema for creating a consultation request."""
    name: str
    email: EmailStr
    phone_number: str
    message: Optional[str] = None
    preferred_contact_method: Optional[str] = "phone"  # phone, email, whatsapp
    preferred_time: Optional[str] = None  # morning, afternoon, evening
    source: Optional[str] = "financial_clinic"  # financial_clinic, website, etc.


class ConsultationRequestUpdate(BaseModel):
    """Schema for updating a consultation request."""
    status: Optional[str] = None  # pending, contacted, scheduled, completed, cancelled
    notes: Optional[str] = None
    contacted_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None


class ConsultationRequestResponse(BaseModel):
    """Schema for consultation request response."""
    id: int
    name: str
    email: str
    phone_number: str
    message: Optional[str]
    preferred_contact_method: str
    preferred_time: Optional[str]
    source: str
    status: str
    notes: Optional[str]
    created_at: datetime
    contacted_at: Optional[datetime]
    scheduled_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConsultationRequestStats(BaseModel):
    """Schema for consultation request statistics."""
    total: int
    pending: int
    contacted: int
    scheduled: int
    completed: int
    this_week: int
    conversion_rate: float  # percentage of requests that became consultations


class ConsultationRequestFilters(BaseModel):
    """Schema for filtering consultation requests."""
    status: Optional[str] = None
    source: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None  # Search by name, email, or phone


class ScheduledEmailCreate(BaseModel):
    """Schema for creating a scheduled email."""
    recipient_emails: list[EmailStr]
    subject: Optional[str] = None
    scheduled_datetime: datetime
    status_filter: Optional[str] = None
    source_filter: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ScheduledEmailResponse(BaseModel):
    """Schema for scheduled email response."""
    id: int
    recipient_emails: list[str]
    subject: str
    scheduled_datetime: datetime
    status_filter: Optional[str]
    source_filter: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    job_id: str
    status: str
    error_message: Optional[str]
    created_by: int
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True

