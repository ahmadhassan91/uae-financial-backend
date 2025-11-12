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
    """Schema for creating a new bilingual question variation."""
    base_question_id: str = Field(..., description="Base question ID")
    variation_name: str = Field(..., min_length=1, max_length=100, description="Variation name")
    language: str = Field("en", pattern="^(en|ar|both)$", description="Language code (deprecated, use both)")
    
    # Bilingual text fields
    text_en: str = Field(..., min_length=1, description="Question text in English")
    text_ar: str = Field(..., min_length=1, description="Question text in Arabic")
    
    # Legacy single text field (optional for backward compatibility)
    text: Optional[str] = Field(None, min_length=1, description="Question text (deprecated)")
    
    # Bilingual options: [{"value": 1, "label_en": "...", "label_ar": "..."}]
    options: List[Dict[str, Any]] = Field(..., description="Question options (bilingual)")
    demographic_rules: Optional[Dict[str, Any]] = Field(None, description="Demographic targeting rules")
    company_ids: Optional[List[int]] = Field(None, description="Company IDs this applies to")
    
    @validator('options')
    def validate_options(cls, v):
        """Validate bilingual options structure."""
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("Options must be a non-empty list")
        
        for i, option in enumerate(v):
            if not isinstance(option, dict):
                raise ValueError(f"Option {i} must be a dictionary")
            
            # Check for required fields
            if 'value' not in option:
                raise ValueError(f"Option {i} must have 'value' field")
            
            # Support both legacy (label) and new bilingual (label_en, label_ar) formats
            has_legacy = 'label' in option
            has_bilingual = 'label_en' in option and 'label_ar' in option
            
            if not has_legacy and not has_bilingual:
                raise ValueError(f"Option {i} must have either 'label' or both 'label_en' and 'label_ar' fields")
            
            if not isinstance(option['value'], int):
                raise ValueError(f"Option {i} value must be an integer")
            
            # Validate labels
            if has_bilingual:
                if not isinstance(option['label_en'], str) or not option['label_en'].strip():
                    raise ValueError(f"Option {i} label_en must be a non-empty string")
                if not isinstance(option['label_ar'], str) or not option['label_ar'].strip():
                    raise ValueError(f"Option {i} label_ar must be a non-empty string")
            elif has_legacy:
                if not isinstance(option['label'], str) or not option['label'].strip():
                    raise ValueError(f"Option {i} label must be a non-empty string")
        
        return v


class QuestionVariationUpdate(BaseModel):
    """Schema for updating a bilingual question variation."""
    variation_name: Optional[str] = Field(None, min_length=1, max_length=100)
    text_en: Optional[str] = Field(None, min_length=1, description="Question text in English")
    text_ar: Optional[str] = Field(None, min_length=1, description="Question text in Arabic")
    text: Optional[str] = Field(None, min_length=1, description="Question text (deprecated)")
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
    """Schema for bilingual question variation response."""
    id: int
    base_question_id: str
    variation_name: str
    language: str
    text_en: Optional[str] = None
    text_ar: Optional[str] = None
    text: Optional[str] = None  # Backward compatibility
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


# Variation Set Schemas
class VariationSetCreate(BaseModel):
    """Schema for creating a new variation set."""
    name: str = Field(..., min_length=1, max_length=255, description="Set name")
    description: Optional[str] = Field(None, description="Set description")
    set_type: str = Field(..., pattern="^(industry|demographic|language|custom)$", description="Set type")
    is_template: bool = Field(False, description="Whether this is a template set")
    is_active: bool = Field(True, description="Whether this set is active")
    
    # All 15 question variation IDs
    q1_variation_id: int = Field(..., gt=0, description="Question 1 variation ID")
    q2_variation_id: int = Field(..., gt=0, description="Question 2 variation ID")
    q3_variation_id: int = Field(..., gt=0, description="Question 3 variation ID")
    q4_variation_id: int = Field(..., gt=0, description="Question 4 variation ID")
    q5_variation_id: int = Field(..., gt=0, description="Question 5 variation ID")
    q6_variation_id: int = Field(..., gt=0, description="Question 6 variation ID")
    q7_variation_id: int = Field(..., gt=0, description="Question 7 variation ID")
    q8_variation_id: int = Field(..., gt=0, description="Question 8 variation ID")
    q9_variation_id: int = Field(..., gt=0, description="Question 9 variation ID")
    q10_variation_id: int = Field(..., gt=0, description="Question 10 variation ID")
    q11_variation_id: int = Field(..., gt=0, description="Question 11 variation ID")
    q12_variation_id: int = Field(..., gt=0, description="Question 12 variation ID")
    q13_variation_id: int = Field(..., gt=0, description="Question 13 variation ID")
    q14_variation_id: int = Field(..., gt=0, description="Question 14 variation ID")
    q15_variation_id: int = Field(..., gt=0, description="Question 15 variation ID")


class VariationSetUpdate(BaseModel):
    """Schema for updating an existing variation set."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Set name")
    description: Optional[str] = Field(None, description="Set description")
    set_type: Optional[str] = Field(None, pattern="^(industry|demographic|language|custom)$", description="Set type")
    is_template: Optional[bool] = Field(None, description="Whether this is a template set")
    is_active: Optional[bool] = Field(None, description="Whether this set is active")
    
    # All 15 question variation IDs (optional for partial updates)
    q1_variation_id: Optional[int] = Field(None, gt=0, description="Question 1 variation ID")
    q2_variation_id: Optional[int] = Field(None, gt=0, description="Question 2 variation ID")
    q3_variation_id: Optional[int] = Field(None, gt=0, description="Question 3 variation ID")
    q4_variation_id: Optional[int] = Field(None, gt=0, description="Question 4 variation ID")
    q5_variation_id: Optional[int] = Field(None, gt=0, description="Question 5 variation ID")
    q6_variation_id: Optional[int] = Field(None, gt=0, description="Question 6 variation ID")
    q7_variation_id: Optional[int] = Field(None, gt=0, description="Question 7 variation ID")
    q8_variation_id: Optional[int] = Field(None, gt=0, description="Question 8 variation ID")
    q9_variation_id: Optional[int] = Field(None, gt=0, description="Question 9 variation ID")
    q10_variation_id: Optional[int] = Field(None, gt=0, description="Question 10 variation ID")
    q11_variation_id: Optional[int] = Field(None, gt=0, description="Question 11 variation ID")
    q12_variation_id: Optional[int] = Field(None, gt=0, description="Question 12 variation ID")
    q13_variation_id: Optional[int] = Field(None, gt=0, description="Question 13 variation ID")
    q14_variation_id: Optional[int] = Field(None, gt=0, description="Question 14 variation ID")
    q15_variation_id: Optional[int] = Field(None, gt=0, description="Question 15 variation ID")


class VariationSetResponse(BaseModel):
    """Schema for variation set response."""
    id: int
    name: str
    description: Optional[str]
    set_type: str
    is_template: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # All 15 question variation IDs
    q1_variation_id: int
    q2_variation_id: int
    q3_variation_id: int
    q4_variation_id: int
    q5_variation_id: int
    q6_variation_id: int
    q7_variation_id: int
    q8_variation_id: int
    q9_variation_id: int
    q10_variation_id: int
    q11_variation_id: int
    q12_variation_id: int
    q13_variation_id: int
    q14_variation_id: int
    q15_variation_id: int
    
    # Statistics (optional)
    companies_using_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class VariationSetListResponse(BaseModel):
    """Schema for paginated variation set list."""
    variation_sets: List[VariationSetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class VariationSetCloneRequest(BaseModel):
    """Schema for cloning a variation set."""
    new_name: str = Field(..., min_length=1, max_length=255, description="New set name")
    new_description: Optional[str] = Field(None, description="New set description")


class CompanySetAssignmentRequest(BaseModel):
    """Schema for assigning a variation set to a company."""
    variation_set_id: int = Field(..., gt=0, description="Variation set ID to assign")


class CompanySetAssignmentResponse(BaseModel):
    """Schema for company set assignment response."""
    company_id: int
    company_name: str
    variation_set_id: Optional[int]
    variation_set_name: Optional[str]
    updated_at: datetime