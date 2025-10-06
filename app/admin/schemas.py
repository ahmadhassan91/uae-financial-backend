"""
Pydantic schemas for admin API endpoints.

This module defines request and response schemas for admin functionality
including question variations, demographic rules, and localization management.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


# Question Variation Schemas
class QuestionVariationCreate(BaseModel):
    """Schema for creating a new question variation."""
    base_question_id: str = Field(..., description="Base question ID")
    variation_name: str = Field(..., min_length=1, max_length=100, description="Variation name")
    language: str = Field("en", pattern="^(en|ar)$", description="Language code")
    text: str = Field(..., min_length=1, description="Question text")
    options: List[Dict[str, Any]] = Field(..., description="Question options")
    demographic_rules: Optional[Dict[str, Any]] = Field(None, description="Demographic targeting rules")
    company_ids: Optional[List[int]] = Field(None, description="Company IDs this applies to")
    
    @validator('options')
    def validate_options(cls, v):
        """Validate options structure."""
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("Options must be a non-empty list")
        
        for i, option in enumerate(v):
            if not isinstance(option, dict):
                raise ValueError(f"Option {i} must be a dictionary")
            if 'value' not in option or 'label' not in option:
                raise ValueError(f"Option {i} must have 'value' and 'label' fields")
            if not isinstance(option['value'], int):
                raise ValueError(f"Option {i} value must be an integer")
            if not isinstance(option['label'], str) or not option['label'].strip():
                raise ValueError(f"Option {i} label must be a non-empty string")
        
        return v


class QuestionVariationUpdate(BaseModel):
    """Schema for updating a question variation."""
    variation_name: Optional[str] = Field(None, min_length=1, max_length=100)
    text: Optional[str] = Field(None, min_length=1)
    options: Optional[List[Dict[str, Any]]] = None
    demographic_rules: Optional[Dict[str, Any]] = None
    company_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None
    
    @validator('options')
    def validate_options(cls, v):
        """Validate options structure if provided."""
        if v is not None:
            return QuestionVariationCreate.validate_options(v)
        return v


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
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuestionVariationListResponse(BaseModel):
    """Schema for paginated question variation list."""
    variations: List[QuestionVariationResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class VariationValidationResult(BaseModel):
    """Schema for variation validation result."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    consistency_score: float = Field(..., ge=0.0, le=1.0)


class VariationTestRequest(BaseModel):
    """Schema for testing a question variation."""
    base_question_id: str
    text: str
    options: List[Dict[str, Any]]
    language: str = "en"
    demographic_rules: Optional[Dict[str, Any]] = None
    test_profiles: Optional[List[Dict[str, Any]]] = None


class VariationTestResult(BaseModel):
    """Schema for variation test result."""
    validation: VariationValidationResult
    profile_matches: List[Dict[str, Any]]
    estimated_usage: int


class QuestionVariationAnalytics(BaseModel):
    """Schema for question variation analytics."""
    total_variations: int
    active_variations: int
    usage_rate: float = Field(..., ge=0.0, le=1.0)
    top_variations: List[Dict[str, Any]]
    language_distribution: Dict[str, int]
    company_specific_variations: int
    analysis_period_days: int


# Demographic Rule Schemas
class DemographicRuleCreate(BaseModel):
    """Schema for creating a demographic rule."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    actions: Dict[str, Any] = Field(..., description="Actions to take when rule matches")
    priority: int = Field(100, ge=1, le=1000, description="Rule priority (lower = higher priority)")
    is_active: bool = Field(True, description="Whether rule is active")


class DemographicRuleUpdate(BaseModel):
    """Schema for updating a demographic rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None


class DemographicRuleResponse(BaseModel):
    """Schema for demographic rule response."""
    id: int
    name: str
    description: Optional[str]
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DemographicRuleListResponse(BaseModel):
    """Schema for paginated demographic rule list."""
    rules: List[DemographicRuleResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class RuleValidationResult(BaseModel):
    """Schema for rule validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str]


class RuleTestRequest(BaseModel):
    """Schema for testing a demographic rule."""
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    test_profiles: List[Dict[str, Any]]


class RuleTestResult(BaseModel):
    """Schema for rule test result."""
    validation: RuleValidationResult
    profile_matches: List[Dict[str, Any]]
    estimated_impact: Dict[str, Any]


class DemographicRuleAnalytics(BaseModel):
    """Schema for demographic rule analytics."""
    total_rules: int
    active_rules: int
    average_priority: float
    rule_effectiveness: List[Dict[str, Any]]
    most_used_conditions: List[Dict[str, Any]]
    analysis_period_days: int


# Localization Schemas
class LocalizedContentCreate(BaseModel):
    """Schema for creating localized content."""
    content_type: str = Field(..., pattern="^(question|recommendation|ui)$")
    content_id: str = Field(..., min_length=1, max_length=100)
    language: str = Field(..., pattern="^(en|ar)$")
    title: Optional[str] = Field(None, max_length=500)
    text: str = Field(..., min_length=1)
    options: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None
    version: str = Field("1.0", pattern="^\\d+\\.\\d+$")


class LocalizedContentUpdate(BaseModel):
    """Schema for updating localized content."""
    title: Optional[str] = Field(None, max_length=500)
    text: Optional[str] = Field(None, min_length=1)
    options: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(None, pattern="^\\d+\\.\\d+$")
    is_active: Optional[bool] = None


class LocalizedContentResponse(BaseModel):
    """Schema for localized content response."""
    id: int
    content_type: str
    content_id: str
    language: str
    title: Optional[str] = None
    text: str
    options: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LocalizedContentListResponse(BaseModel):
    """Schema for paginated localized content list."""
    content: List[LocalizedContentResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class TranslationWorkflowRequest(BaseModel):
    """Schema for translation workflow request."""
    content_ids: List[str]
    source_language: str = "en"
    target_language: str = "ar"
    workflow_type: str = Field("manual", pattern="^(manual|automatic|hybrid)$")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    notes: Optional[str] = None


class TranslationWorkflowResponse(BaseModel):
    """Schema for translation workflow response."""
    workflow_id: str
    status: str
    content_items: List[Dict[str, Any]]
    estimated_completion: Optional[datetime]
    assigned_translator: Optional[str]
    created_at: datetime


class LocalizationAnalytics(BaseModel):
    """Schema for localization analytics."""
    total_content_items: int
    translated_items: int
    translation_coverage: Dict[str, float]
    pending_translations: int
    quality_scores: Dict[str, float]
    most_requested_content: List[Dict[str, Any]]
    analysis_period_days: int


# System Analytics Schemas
class SystemAnalyticsOverview(BaseModel):
    """Schema for system analytics overview."""
    question_variations: QuestionVariationAnalytics
    demographic_rules: DemographicRuleAnalytics
    localization: LocalizationAnalytics
    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]


# Bulk Operations Schemas
class BulkOperationRequest(BaseModel):
    """Schema for bulk operations."""
    operation: str = Field(..., pattern="^(activate|deactivate|delete|export)$")
    entity_type: str = Field(..., pattern="^(question_variation|demographic_rule|localized_content)$")
    entity_ids: List[int]
    parameters: Optional[Dict[str, Any]] = None


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response."""
    operation_id: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int
    errors: List[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]


# Export Schemas
class ExportRequest(BaseModel):
    """Schema for data export request."""
    entity_type: str = Field(..., pattern="^(question_variation|demographic_rule|localized_content|analytics)$")
    format: str = Field("csv", pattern="^(csv|excel|json)$")
    filters: Optional[Dict[str, Any]] = None
    include_usage_data: bool = Field(False)
    date_range: Optional[Dict[str, str]] = None


class ExportResponse(BaseModel):
    """Schema for export response."""
    export_id: str
    status: str
    file_url: Optional[str]
    file_size: Optional[int]
    record_count: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]