"""Database models for the UAE Financial Health Check application."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Import PDPL-compliant consent models
from app.models_consent import (
    UserConsent,
    ConsentAuditLog,
    DataProcessingActivity,
    DataSubjectRequest
)


class User(Base):
    """User model for authentication and basic user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)  # For profile data (not auth)
    email_verified = Column(Boolean, default=False)  # For OTP verification
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    admin_role = Column(String(20), default="full", nullable=False)  # "full" or "view_only"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer_profiles = relationship("CustomerProfile", back_populates="user")
    survey_responses = relationship("SurveyResponse", back_populates="user")


class CustomerProfile(Base):
    """Customer profile model with personal and demographic information."""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False, index=True)
    gender = Column(String(20), nullable=False)
    nationality = Column(String(100), nullable=False, index=True)
    
    # Location
    emirate = Column(String(50), nullable=False, index=True)
    city = Column(String(100), nullable=True)
    
    # Employment
    employment_status = Column(String(50), nullable=False)
    industry = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # Financial Information
    monthly_income = Column(String(50), nullable=False)  # Income range
    household_size = Column(Integer, nullable=False)
    
    # Family Information
    children = Column(String(3), nullable=False, default="No")  # "Yes" or "No"
    
    # Additional Information
    phone_number = Column(String(20), nullable=True)
    preferred_language = Column(String(10), default="en")
    
    # Enhanced demographic fields for advanced features
    education_level = Column(String(50), nullable=True)
    years_in_uae = Column(Integer, nullable=True)  # For expats
    family_status = Column(String(50), nullable=True)
    housing_status = Column(String(50), nullable=True)  # own, rent, family
    
    # Financial context
    banking_relationship = Column(String(100), nullable=True)
    investment_experience = Column(String(50), nullable=True)
    financial_goals = Column(JSON, nullable=True)
    
    # Preferences
    preferred_communication = Column(String(20), default="email")
    islamic_finance_preference = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="customer_profiles")
    survey_responses = relationship("SurveyResponse", back_populates="customer_profile")


class SurveyResponse(Base):
    """Survey response model storing user answers and calculated scores."""
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_profile_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)
    
    # Survey data
    responses = Column(JSON, nullable=False)  # Store all question responses as JSON
    
    # Calculated scores (0-100 scale)
    overall_score = Column(Float, nullable=False)
    budgeting_score = Column(Float, nullable=False)
    savings_score = Column(Float, nullable=False)
    debt_management_score = Column(Float, nullable=False)
    financial_planning_score = Column(Float, nullable=False)
    investment_knowledge_score = Column(Float, nullable=False)
    
    # Risk assessment
    risk_tolerance = Column(String(20), nullable=False)  # low, moderate, high
    financial_goals = Column(JSON, nullable=True)  # Array of goals
    
    # Metadata
    completion_time = Column(Integer, nullable=True)  # Time in seconds
    survey_version = Column(String(10), default="1.0")
    
    # Enhanced metadata for advanced features
    question_set_id = Column(String(100), nullable=True)
    question_variations_used = Column(JSON, nullable=True)
    demographic_rules_applied = Column(JSON, nullable=True)
    language = Column(String(5), default="en", index=True)
    
    # Company context
    company_tracker_id = Column(Integer, ForeignKey("company_trackers.id"), nullable=True, index=True)
    
    # Report delivery tracking
    email_sent = Column(Boolean, default=False)
    pdf_generated = Column(Boolean, default=False)
    report_downloads = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="survey_responses")
    customer_profile = relationship("CustomerProfile", back_populates="survey_responses")
    recommendations = relationship("Recommendation", back_populates="survey_response")
    company_tracker = relationship("CompanyTracker")


class Recommendation(Base):
    """Personalized recommendations based on survey responses."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    survey_response_id = Column(Integer, ForeignKey("survey_responses.id"), nullable=False)
    
    # Recommendation details
    category = Column(String(50), nullable=False)  # budgeting, savings, debt, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)  # 1 = high, 2 = medium, 3 = low
    
    # Implementation details
    action_steps = Column(JSON, nullable=True)  # Array of actionable steps
    resources = Column(JSON, nullable=True)  # Links, documents, tools
    expected_impact = Column(String(20), nullable=True)  # high, medium, low
    
    # Tracking
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    survey_response = relationship("SurveyResponse", back_populates="recommendations")


class CompanyTracker(Base):
    """Company tracking for HR departments and bulk assessments."""
    __tablename__ = "company_trackers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company information
    company_name = Column(String(200), nullable=False)
    company_email = Column(String(255), nullable=False)
    contact_person = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=True)
    
    # Tracking details
    unique_url = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_assessments = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    
    # Settings
    custom_branding = Column(JSON, nullable=True)  # Logo, colors, etc.
    notification_settings = Column(JSON, nullable=True)
    
    # Enhanced company-specific fields for advanced features
    question_set_config = Column(JSON, nullable=True)  # Custom question sets
    demographic_rules_config = Column(JSON, nullable=True)  # Company-specific rules
    localization_settings = Column(JSON, nullable=True)  # Language preferences
    report_branding = Column(JSON, nullable=True)  # Custom report branding
    admin_users = Column(JSON, nullable=True)  # Company admin user IDs
    
    # Variation Set Assignment
    variation_set_id = Column(Integer, ForeignKey("variation_sets.id"), nullable=True, index=True)
    
    # Variation Control Flags
    enable_variations = Column(Boolean, default=False, index=True)  # Explicit control for variations
    variations_enabled_at = Column(DateTime(timezone=True), nullable=True)
    variations_enabled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Question Variation Mapping (API compatibility)
    question_variation_mapping = Column(JSON, nullable=True)  # {"fc_q3": 123, "fc_q11": 456}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company_assessments = relationship("CompanyAssessment", back_populates="company_tracker")
    variation_set = relationship("VariationSet")
    incomplete_surveys = relationship("IncompleteSurvey", back_populates="company")


class CompanyAssessment(Base):
    """Individual assessments completed through company tracking."""
    __tablename__ = "company_assessments"

    id = Column(Integer, primary_key=True, index=True)
    company_tracker_id = Column(Integer, ForeignKey("company_trackers.id"), nullable=False)
    
    # Anonymous employee data
    employee_id = Column(String(100), nullable=True)  # Optional anonymous ID
    department = Column(String(100), nullable=True)
    position_level = Column(String(50), nullable=True)  # junior, mid, senior, executive
    
    # Assessment data (similar to SurveyResponse but company-focused)
    responses = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False)
    category_scores = Column(JSON, nullable=False)  # Detailed breakdown
    
    # Metadata
    completion_time = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)  # For basic analytics
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company_tracker = relationship("CompanyTracker", back_populates="company_assessments")


class SimpleSession(Base):
    """Simple authentication sessions for email + DOB login."""
    __tablename__ = "simple_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class IncompleteSurvey(Base):
    """Track incomplete/abandoned survey sessions for follow-up."""
    __tablename__ = "incomplete_surveys"

    id = Column(Integer, primary_key=True, index=True)
    
    # User information (can be null for guest users)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_profile_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=True)
    
    # Company tracking (for surveys started via company QR codes)
    company_id = Column(Integer, ForeignKey("company_trackers.id"), nullable=True)
    company_url = Column(String(255), nullable=True, index=True)
    
    # Session tracking
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Survey progress
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, nullable=False)
    responses = Column(JSON, nullable=True)  # Partial responses
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    abandoned_at = Column(DateTime(timezone=True), nullable=True)  # Set when considered abandoned
    
    # Contact information for follow-up (for guest users)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Status
    is_abandoned = Column(Boolean, default=False)
    follow_up_sent = Column(Boolean, default=False)
    follow_up_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    customer_profile = relationship("CustomerProfile")
    company = relationship("CompanyTracker", back_populates="incomplete_surveys")


class AuditLog(Base):
    """Audit trail for important system actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User and action details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # login, survey_complete, profile_update
    entity_type = Column(String(50), nullable=True)  # user, survey, profile
    entity_id = Column(Integer, nullable=True)
    
    # Additional context
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class QuestionVariation(Base):
    """Different variations of questions for demographic/company customization."""
    __tablename__ = "question_variations"
    
    id = Column(Integer, primary_key=True, index=True)
    base_question_id = Column(String(50), nullable=False, index=True)  # e.g., "fc_q1"
    variation_name = Column(String(100), nullable=False)  # e.g., "uae_citizen_version"
    language = Column(String(5), nullable=False, default="en", index=True)  # DEPRECATED: kept for compatibility
    
    # Question content - BILINGUAL (new structure)
    text_en = Column(Text, nullable=True)  # English text
    text_ar = Column(Text, nullable=True)  # Arabic text
    text = Column(Text, nullable=True)  # DEPRECATED: old single-language field
    
    # Options - BILINGUAL (new structure)
    # Format: [{"value": 1, "label_en": "...", "label_ar": "..."}]
    options = Column(JSON, nullable=False)  # Array of {value, label_en, label_ar}
    
    # Targeting rules
    demographic_rules = Column(JSON, nullable=True)  # Conditions for when to use
    company_ids = Column(JSON, nullable=True)  # Specific companies
    
    # Metadata
    factor = Column(String(50), nullable=False)
    weight = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VariationSet(Base):
    """Bundles of question variations that can be assigned to companies."""
    __tablename__ = "variation_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    set_type = Column(String(50), nullable=False, index=True)  # 'industry', 'demographic', 'language', 'custom'
    is_template = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Foreign keys for all 15 Financial Clinic questions
    q1_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q2_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q3_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q4_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q5_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q6_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q7_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q8_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q9_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q10_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q11_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q12_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q13_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q14_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    q15_variation_id = Column(Integer, ForeignKey("question_variations.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    q1_variation = relationship("QuestionVariation", foreign_keys=[q1_variation_id])
    q2_variation = relationship("QuestionVariation", foreign_keys=[q2_variation_id])
    q3_variation = relationship("QuestionVariation", foreign_keys=[q3_variation_id])
    q4_variation = relationship("QuestionVariation", foreign_keys=[q4_variation_id])
    q5_variation = relationship("QuestionVariation", foreign_keys=[q5_variation_id])
    q6_variation = relationship("QuestionVariation", foreign_keys=[q6_variation_id])
    q7_variation = relationship("QuestionVariation", foreign_keys=[q7_variation_id])
    q8_variation = relationship("QuestionVariation", foreign_keys=[q8_variation_id])
    q9_variation = relationship("QuestionVariation", foreign_keys=[q9_variation_id])
    q10_variation = relationship("QuestionVariation", foreign_keys=[q10_variation_id])
    q11_variation = relationship("QuestionVariation", foreign_keys=[q11_variation_id])
    q12_variation = relationship("QuestionVariation", foreign_keys=[q12_variation_id])
    q13_variation = relationship("QuestionVariation", foreign_keys=[q13_variation_id])
    q14_variation = relationship("QuestionVariation", foreign_keys=[q14_variation_id])
    q15_variation = relationship("QuestionVariation", foreign_keys=[q15_variation_id])


class DemographicRule(Base):
    """Rules for determining which questions to show based on demographics."""
    __tablename__ = "demographic_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule conditions (JSON with complex logic)
    conditions = Column(JSON, nullable=False)
    # Example: {
    #   "and": [
    #     {"nationality": {"eq": "UAE"}},
    #     {"age": {"gte": 25}},
    #     {"or": [
    #       {"emirate": {"in": ["Dubai", "Abu Dhabi"]}},
    #       {"income": {"gte": "10000"}}
    #     ]}
    #   ]
    # }
    
    # Actions to take when rule matches
    actions = Column(JSON, nullable=False)
    # Example: {
    #   "include_questions": ["q1_uae_version", "q2_citizen_version"],
    #   "exclude_questions": ["q1_expat_version"],
    #   "add_questions": ["q17_zakat_planning"]
    # }
    
    priority = Column(Integer, default=100, index=True)  # Lower = higher priority
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LocalizedContent(Base):
    """Localized content for questions, recommendations, and UI elements."""
    __tablename__ = "localized_content"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # question, recommendation, ui
    content_id = Column(String(100), nullable=False, index=True)  # question_id, recommendation_id, ui_key
    language = Column(String(5), nullable=False, index=True)
    
    # Content fields
    title = Column(String(500), nullable=True)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For questions
    extra_data = Column(JSON, nullable=True)  # Additional localized data
    
    # Versioning
    version = Column(String(10), default="1.0")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportDelivery(Base):
    """Track email and PDF report deliveries."""
    __tablename__ = "report_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_response_id = Column(Integer, ForeignKey("survey_responses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Delivery details
    delivery_type = Column(String(20), nullable=False, index=True)  # email, pdf_download
    delivery_status = Column(String(20), nullable=False, index=True)  # pending, sent, failed, downloaded
    recipient_email = Column(String(255), nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=True)  # For PDF files
    file_size = Column(Integer, nullable=True)  # File size in bytes
    language = Column(String(5), nullable=False, default="en")
    
    # Metadata and error handling
    delivery_metadata = Column(JSON, nullable=True)  # Additional delivery info
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    survey_response = relationship("SurveyResponse")
    user = relationship("User")
    access_logs = relationship("ReportAccessLog", back_populates="report_delivery")


class ReportAccessLog(Base):
    """Track report downloads, views, and email opens."""
    __tablename__ = "report_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    report_delivery_id = Column(Integer, ForeignKey("report_deliveries.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Can be null for anonymous access
    
    # Access details
    access_type = Column(String(20), nullable=False)  # download, view, email_open
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    access_metadata = Column(JSON, nullable=True)  # Additional access info
    
    # Timestamp
    accessed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    report_delivery = relationship("ReportDelivery", back_populates="access_logs")
    user = relationship("User")


class CompanyQuestionSet(Base):
    """Custom question sets for specific companies/URLs."""
    __tablename__ = "company_question_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    company_tracker_id = Column(Integer, ForeignKey("company_trackers.id"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Question configuration
    base_questions = Column(JSON, nullable=False)  # Base question IDs
    custom_questions = Column(JSON, nullable=True)  # Company-specific additions
    excluded_questions = Column(JSON, nullable=True)  # Questions to skip
    question_variations = Column(JSON, nullable=True)  # Variation mappings
    
    # Demographic rules specific to this company
    demographic_rules = Column(JSON, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company_tracker = relationship("CompanyTracker")


class Product(Base):
    """Product recommendations for Financial Clinic system."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Product details
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # Income Stream, Savings Habit, etc.
    status_level = Column(String(50), nullable=False, index=True)  # at_risk, good, excellent
    description = Column(Text, nullable=False)
    
    # Demographic filters (NULL means "applies to all")
    nationality_filter = Column(String(50), nullable=True, index=True)  # "Emirati", "Non-Emirati", or NULL
    gender_filter = Column(String(20), nullable=True, index=True)  # "Male", "Female", or NULL
    children_filter = Column(String(20), nullable=True)  # "0", "1+", or NULL
    
    # Priority and status
    priority = Column(Integer, default=1, index=True)  # Lower number = higher priority
    active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def matches_demographics(
        self,
        nationality: str,
        gender: Optional[str] = None,
        children: int = 0
    ) -> bool:
        """
        Check if product matches user demographics.
        
        Args:
            nationality: User nationality ("Emirati" or "Non-Emirati")
            gender: User gender ("Male" or "Female")
            children: Number of children (0-5+)
            
        Returns:
            True if product matches all applicable filters
        """
        # Check nationality filter
        if self.nationality_filter and self.nationality_filter != nationality:
            return False
        
        # Check gender filter
        if self.gender_filter and gender and self.gender_filter != gender:
            return False
        
        # Check children filter
        if self.children_filter:
            if self.children_filter == "0" and children > 0:
                return False
            if self.children_filter == "1+" and children == 0:
                return False
        
        return True


class FinancialClinicProfile(Base):
    """
    Financial Clinic customer profile.
    Stores demographic and contact information for Financial Clinic assessments.
    This is separate from CustomerProfile to allow standalone Financial Clinic usage.
    """
    __tablename__ = "financial_clinic_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Required Personal Information
    name = Column(String(200), nullable=False)
    date_of_birth = Column(String(20), nullable=False)  # Format: DD/MM/YYYY
    gender = Column(String(20), nullable=False, index=True)  # Male, Female
    nationality = Column(String(50), nullable=False, index=True)  # Emirati, Non-Emirati
    
    # Family Information
    children = Column(Integer, nullable=False, default=0, index=True)  # 0-5+
    
    # Employment & Income
    employment_status = Column(String(50), nullable=False, index=True)  # Employed, Self-Employed, Unemployed
    income_range = Column(String(50), nullable=False, index=True)  # Below 5K, 5K-10K, etc.
    
    # Location
    emirate = Column(String(100), nullable=False, index=True)  # Dubai, Abu Dhabi, etc.
    
    # Contact Information
    email = Column(String(255), nullable=False, index=True)
    mobile_number = Column(String(20), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    survey_responses = relationship("FinancialClinicResponse", back_populates="profile")


class FinancialClinicResponse(Base):
    """
    Financial Clinic survey response.
    Stores answers and calculated results for Financial Clinic assessments.
    """
    __tablename__ = "financial_clinic_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("financial_clinic_profiles.id"), nullable=False, index=True)
    
    # Company Tracking (optional - for corporate assessments)
    company_tracker_id = Column(Integer, ForeignKey("company_trackers.id"), nullable=True, index=True)
    
    # Survey Data
    answers = Column(JSON, nullable=False)  # {question_id: answer_value}
    
    # Calculated Results
    total_score = Column(Float, nullable=False, index=True)  # 0-100
    status_band = Column(String(50), nullable=False, index=True)  # At Risk, Good, Excellent, etc.
    category_scores = Column(JSON, nullable=False)  # Detailed category breakdown
    
    # Recommendations
    insights = Column(JSON, nullable=True)  # Selected insights
    product_recommendations = Column(JSON, nullable=True)  # Recommended products
    
    # Metadata
    questions_answered = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When the survey was completed
    
    # Relationships
    profile = relationship("FinancialClinicProfile", back_populates="survey_responses")
    company_tracker = relationship("CompanyTracker")


class OTPCode(Base):
    """OTP codes for email verification and authentication."""
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempt_count = Column(Integer, default=0, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)


class ConsultationRequest(Base):
    """Consultation requests from users who want to book a free consultation."""
    __tablename__ = "consultation_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    
    # Request details
    message = Column(Text, nullable=True)
    preferred_contact_method = Column(String(20), default="phone", nullable=False)  # phone, email, whatsapp
    preferred_time = Column(String(20), nullable=True)  # morning, afternoon, evening
    source = Column(String(50), default="financial_clinic", nullable=False)  # financial_clinic, website, etc.
    
    # Status tracking
    status = Column(String(20), default="pending", nullable=False)  # pending, contacted, scheduled, completed, cancelled
    notes = Column(Text, nullable=True)  # Admin notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_consultation_status', 'status'),
        Index('idx_consultation_source', 'source'),
        Index('idx_consultation_created_at', 'created_at'),
        Index('idx_consultation_email', 'email'),
    )


class ScheduledEmail(Base):
    """Scheduled email jobs for sending CSV exports of consultation leads."""
    __tablename__ = "scheduled_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Email configuration
    recipient_emails = Column(JSON, nullable=False)  # List of email addresses
    subject = Column(String(255), nullable=False)
    scheduled_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Filters for leads data export (same as export endpoint)
    status_filter = Column(String(20), nullable=True)
    source_filter = Column(String(50), nullable=True)
    date_from = Column(DateTime(timezone=True), nullable=True)
    date_to = Column(DateTime(timezone=True), nullable=True)
    
    # Job tracking
    job_id = Column(String(255), unique=True, index=True, nullable=False)  # APScheduler job ID
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, sent, failed, cancelled
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User")

