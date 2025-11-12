"""Pydantic schemas for company management."""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime


class CompanyBase(BaseModel):
    company_name: str
    company_email: EmailStr
    contact_person: str
    phone_number: Optional[str] = None
    custom_branding: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    question_variation_mapping: Optional[Dict[str, int]] = None  # {"fc_q3": 123, "fc_q11": 456}


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    phone_number: Optional[str] = None
    custom_branding: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    question_variation_mapping: Optional[Dict[str, int]] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    unique_url: str
    is_active: bool
    total_assessments: int
    average_score: Optional[float]
    question_variation_mapping: Optional[Dict[str, int]] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CompanyLinkConfig(BaseModel):
    """Schema for configuring company links."""
    prefix: Optional[str] = None
    expiry_days: Optional[int] = 30
    max_responses: Optional[int] = 1000
    custom_branding: Optional[bool] = False


class CompanyLink(BaseModel):
    """Schema for generated company link."""
    company_id: int
    url: str
    qr_code_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    max_responses: Optional[int] = None


class CompanyAnalytics(BaseModel):
    """Schema for company analytics."""
    company_id: int
    company_name: str
    total_employees: Optional[int] = None
    total_responses: int
    participation_rate: Optional[float] = None
    average_score: Optional[float] = None
    industry_average: Optional[float] = None
    national_average: Optional[float] = None
    age_distribution: Optional[Dict[str, int]] = None
    gender_distribution: Optional[Dict[str, int]] = None
    department_distribution: Optional[Dict[str, int]] = None
    at_risk_employees: int = 0
    improvement_needed: int = 0
    good_health: int = 0
    excellent_health: int = 0


class BulkCompanyCreate(BaseModel):
    """Schema for bulk company creation."""
    companies: List[CompanyCreate]
    default_config: Optional[CompanyLinkConfig] = None


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""
    successful: int
    failed: int
    errors: List[Dict[str, str]]
    generated_links: Optional[List[CompanyLink]] = None
