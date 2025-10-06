"""Pydantic schemas for survey management."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator


class SurveyResponseCreate(BaseModel):
    """Schema for creating a survey response."""
    responses: Dict[str, Any]  # Question ID -> Answer mapping
    completion_time: Optional[int] = None  # Time in seconds
    
    @validator('responses')
    def validate_responses(cls, v):
        if not v:
            raise ValueError('Survey responses cannot be empty')
        return v


class SurveyResponseUpdate(BaseModel):
    """Schema for updating a survey response."""
    responses: Optional[Dict[str, Any]] = None
    completion_time: Optional[int] = None


class ScoreBreakdown(BaseModel):
    """Schema for detailed score breakdown."""
    overall_score: float
    budgeting_score: float
    savings_score: float
    debt_management_score: float
    financial_planning_score: float
    investment_knowledge_score: float
    risk_tolerance: str
    financial_goals: Optional[List[str]] = None


class SurveyResponseResponse(BaseModel):
    """Schema for survey response in API responses."""
    id: int
    user_id: int
    customer_profile_id: int
    responses: Dict[str, Any]
    overall_score: float
    budgeting_score: float
    savings_score: float
    debt_management_score: float
    financial_planning_score: float
    investment_knowledge_score: float
    risk_tolerance: str
    financial_goals: Optional[List[str]]
    completion_time: Optional[int]
    survey_version: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema for recommendation in API responses."""
    id: int
    category: str
    title: str
    description: str
    priority: int
    action_steps: Optional[List[str]]
    resources: Optional[List[Dict[str, str]]]
    expected_impact: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SurveyResultResponse(BaseModel):
    """Schema for complete survey results with recommendations."""
    survey_response: SurveyResponseResponse
    recommendations: List[RecommendationResponse]
    score_breakdown: ScoreBreakdown


class SurveyHistoryResponse(BaseModel):
    """Schema for survey history listing."""
    id: int
    overall_score: float
    created_at: datetime
    survey_version: str
    
    class Config:
        from_attributes = True


class ScorePreviewRequest(BaseModel):
    """Schema for score preview calculation request."""
    responses: Dict[str, Any]  # Question ID -> Answer mapping
    profile: Optional[Dict[str, Any]] = None  # User profile data (e.g., children field)
    
    @validator('responses')
    def validate_responses(cls, v):
        if not v:
            raise ValueError('Survey responses cannot be empty')
        return v


class PillarScore(BaseModel):
    """Schema for individual pillar score."""
    factor: str
    name: str
    score: float
    max_score: int
    percentage: int
    weight: int


class ScorePreviewResponse(BaseModel):
    """Schema for score preview calculation response."""
    total_score: int
    max_possible_score: int
    pillar_scores: List[PillarScore]
    weighted_sum: float
    total_weight: int
    average_score: float
