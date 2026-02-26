from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class CRMScores(BaseModel):
    total_score: float = Field(..., description="Overall financial health score")
    status_band: str = Field(..., description="Classification of financial health")
    income_stream: float = 0.0
    savings_habit: float = 0.0
    debt_management: float = 0.0
    retirement_planning: float = 0.0
    financial_protection: float = 0.0
    financial_knowledge: float = 0.0

class CRMEngagement(BaseModel):
    questions_answered: int
    total_questions: int
    completion_percentage: float
    leads_requested: str  # "Y" or "N"

class CRMActionPlans(BaseModel):
    plan_1: str = ""
    plan_2: str = ""
    plan_3: str = ""
    plan_4: str = ""
    plan_5: str = ""

class CRMConsultation(BaseModel):
    status: Optional[str] = None
    source: Optional[str] = None
    preferred_method: Optional[str] = None
    preferred_time: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None

class CRMTimestamps(BaseModel):
    submission_date: Optional[datetime] = None

class CRMRecord(BaseModel):
    id: Union[int, str]
    type: str  # "Submitted", "Lead", "Incomplete"
    name: Optional[str] = ""
    email: Optional[str] = ""
    mobile_number: Optional[str] = ""
    age: Optional[Union[int, str]] = ""
    gender: Optional[str] = ""
    nationality: Optional[str] = ""
    emirate: Optional[str] = ""
    children: Optional[str] = ""
    employment_status: Optional[str] = ""
    income_range: Optional[str] = ""
    company: Optional[str] = ""
    unique_url: Optional[str] = ""
    scores: Optional[CRMScores] = None
    engagement: Optional[CRMEngagement] = None
    action_plans: Optional[CRMActionPlans] = None
    consultation: Optional[CRMConsultation] = None
    timestamps: Optional[CRMTimestamps] = None

class CRMMeta(BaseModel):
    total_count: int
    timestamp: datetime

class CRMConsolidatedResponse(BaseModel):
    meta: CRMMeta
    data: List[CRMRecord]

class CRMAPIKeyBase(BaseModel):
    name: str

class CRMAPIKeyCreate(CRMAPIKeyBase):
    pass

class CRMAPIKeyResponse(CRMAPIKeyBase):
    id: int
    masked_key: str
    is_active: bool
    created_at: datetime
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CRMAPIKeyNew(CRMAPIKeyResponse):
    plain_key: str  # Only returned once during creation
