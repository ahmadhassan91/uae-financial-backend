"""Schemas for company question management."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionSetCreate(BaseModel):
    """Schema for creating a new question set."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    base_questions: List[str] = Field(..., min_items=1)
    custom_questions: Optional[List[Dict[str, Any]]] = None
    excluded_questions: Optional[List[str]] = None
    question_variations: Optional[Dict[str, str]] = None
    demographic_rules: Optional[List[Dict[str, Any]]] = None


class QuestionSetUpdate(BaseModel):
    """Schema for updating a question set."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    base_questions: Optional[List[str]] = None
    custom_questions: Optional[List[Dict[str, Any]]] = None
    excluded_questions: Optional[List[str]] = None
    question_variations: Optional[Dict[str, str]] = None
    demographic_rules: Optional[List[Dict[str, Any]]] = None


class QuestionSetResponse(BaseModel):
    """Schema for question set response."""
    id: int
    company_tracker_id: int
    name: str
    description: Optional[str]
    base_questions: List[str]
    custom_questions: Optional[List[Dict[str, Any]]]
    excluded_questions: Optional[List[str]]
    question_variations: Optional[Dict[str, str]]
    demographic_rules: Optional[List[Dict[str, Any]]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CompanyQuestionSetConfig(BaseModel):
    """Schema for company question set configuration."""
    questions: List[Dict[str, Any]]
    question_set_id: str
    company_config: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


class QuestionSetAnalytics(BaseModel):
    """Schema for question set analytics."""
    total_responses: int
    average_score: float
    question_performance: Dict[str, Dict[str, Any]]
    demographic_breakdown: Dict[str, Dict[str, Any]]
    score_distribution: Dict[str, int]


class QuestionVariationCreate(BaseModel):
    """Schema for creating question variations."""
    base_question_id: str
    variation_name: str
    language: str = "en"
    text: str
    options: List[Dict[str, Any]]
    demographic_rules: Optional[Dict[str, Any]] = None
    company_ids: Optional[List[int]] = None
    factor: str
    weight: int


class QuestionVariationResponse(BaseModel):
    """Schema for question variation response."""
    id: int
    base_question_id: str
    variation_name: str
    language: str
    text: str
    options: List[Dict[str, Any]]
    demographic_rules: Optional[Dict[str, Any]]
    company_ids: Optional[List[int]]
    factor: str
    weight: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CompanyQuestionPreview(BaseModel):
    """Schema for previewing company question sets."""
    company_url: str
    demographic_profile: Optional[Dict[str, Any]] = None
    language: str = "en"


class QuestionSetVersion(BaseModel):
    """Schema for question set version information."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    total_questions: int
    changes_summary: Optional[str] = None


class QuestionSetComparison(BaseModel):
    """Schema for comparing question sets."""
    version_a: QuestionSetVersion
    version_b: QuestionSetVersion
    added_questions: List[str]
    removed_questions: List[str]
    modified_questions: List[str]
    variation_changes: Dict[str, Dict[str, str]]


class BulkQuestionSetOperation(BaseModel):
    """Schema for bulk operations on question sets."""
    company_ids: List[int]
    operation: str  # "activate", "deactivate", "duplicate"
    source_question_set_id: Optional[int] = None
    new_name_template: Optional[str] = None


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""
    successful: int
    failed: int
    errors: List[Dict[str, str]]
    created_question_sets: Optional[List[QuestionSetResponse]] = None