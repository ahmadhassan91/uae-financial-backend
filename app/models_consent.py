"""
PDPL-Compliant Consent Management Models
UAE Federal Decree-Law No. 45/2021 (Personal Data Protection Law)
"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserConsent(Base):
    """
    PDPL Article 18 Compliant Consent Records
    Stores explicit consent for data processing and profiling activities
    """
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, index=True)
    
    # User identification (can be null for pre-registration consent)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)  # Track anonymous sessions
    
    # Consent details
    consent_type = Column(String(50), nullable=False, index=True)  # 'profiling', 'data_processing', 'marketing', etc.
    granted = Column(Boolean, nullable=False)
    
    # PDPL Requirements
    consent_version = Column(String(20), nullable=False)  # Track consent text version
    consent_text = Column(Text, nullable=False)  # Store actual consent text shown to user
    consent_language = Column(String(10), nullable=False)  # 'en' or 'ar'
    
    # Audit trail (PDPL Article 8 - Accountability)
    granted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/device information
    
    # Withdrawal tracking (PDPL Article 18.3 - Right to Withdraw)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    withdrawal_reason = Column(Text, nullable=True)
    
    # Expiry (PDPL Article 18.4 - Time-limited consent)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Additional metadata
    source_page = Column(String(255), nullable=True)  # Where consent was granted
    consent_metadata = Column(JSON, nullable=True)  # Additional context
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="consents")


class ConsentAuditLog(Base):
    """
    Comprehensive audit log for all consent-related actions
    PDPL Article 8 - Data Controller Accountability
    """
    __tablename__ = "consent_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    consent_id = Column(Integer, ForeignKey("user_consents.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Action details
    action = Column(String(50), nullable=False)  # 'granted', 'withdrawn', 'viewed', 'exported'
    action_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Audit information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    geolocation = Column(String(100), nullable=True)  # Country/Emirate
    
    # Details
    description = Column(Text, nullable=True)
    audit_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    consent = relationship("UserConsent", backref="audit_logs")
    user = relationship("User")


class DataProcessingActivity(Base):
    """
    Register of processing activities (PDPL Article 8)
    Required for demonstrating compliance
    """
    __tablename__ = "data_processing_activities"

    id = Column(Integer, primary_key=True, index=True)
    
    activity_name = Column(String(200), nullable=False)
    activity_description = Column(Text, nullable=False)
    
    # Legal basis (PDPL Article 5)
    legal_basis = Column(String(50), nullable=False)  # 'consent', 'contract', 'legal_obligation', etc.
    consent_type_required = Column(String(50), nullable=True)  # Links to UserConsent.consent_type
    
    # Data categories
    data_categories = Column(JSON, nullable=False)  # List of data types processed
    data_subjects = Column(JSON, nullable=False)  # Categories of individuals
    
    # Processing details
    purpose = Column(Text, nullable=False)
    retention_period = Column(String(100), nullable=False)
    
    # Security measures (PDPL Article 9)
    security_measures = Column(JSON, nullable=False)
    
    # Third-party sharing (PDPL Article 11)
    third_party_sharing = Column(Boolean, default=False)
    third_parties = Column(JSON, nullable=True)
    
    # Cross-border transfer (PDPL Article 15)
    cross_border_transfer = Column(Boolean, default=False)
    transfer_countries = Column(JSON, nullable=True)
    transfer_safeguards = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataSubjectRequest(Base):
    """
    Track data subject rights requests (PDPL Chapter 4)
    - Right to access (Article 13)
    - Right to rectification (Article 14)
    - Right to erasure (Article 15)
    - Right to data portability (Article 16)
    """
    __tablename__ = "data_subject_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Request details
    request_type = Column(String(50), nullable=False, index=True)  # 'access', 'rectification', 'erasure', 'portability'
    request_description = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(String(50), nullable=False, default='pending')  # 'pending', 'in_progress', 'completed', 'rejected'
    
    # PDPL requires response within 30 days (Article 13.3)
    requested_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)  # 30 days from request
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing details
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin/DPO
    processing_notes = Column(Text, nullable=True)
    
    # Response
    response = Column(Text, nullable=True)
    response_file_path = Column(String(500), nullable=True)  # For data exports
    
    # Rejection details (if applicable)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="data_requests")
    assigned_admin = relationship("User", foreign_keys=[assigned_to])
