"""
PDPL-Compliant Consent Management API
UAE Federal Decree-Law No. 45/2021
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

from app.database import get_db
from app.models_consent import UserConsent, ConsentAuditLog
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/consent", tags=["consent"])


# Pydantic Models
class ConsentGrantRequest(BaseModel):
    """Request model for granting consent"""
    consent_type: str = Field(..., description="Type of consent: 'profiling', 'data_processing', 'marketing'")
    consent_version: str = Field(default="1.0", description="Version of consent text")
    consent_language: str = Field(..., description="Language of consent: 'en' or 'ar'")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    source_page: Optional[str] = Field(None, description="Page where consent was granted")


class ConsentResponse(BaseModel):
    """Response model for consent operations"""
    id: int
    consent_type: str
    granted: bool
    granted_at: datetime
    consent_version: str
    consent_language: str
    is_active: bool
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConsentStatusResponse(BaseModel):
    """Response model for checking consent status"""
    has_profiling_consent: bool
    has_data_processing_consent: bool
    has_marketing_consent: bool
    consents: List[ConsentResponse]


class WithdrawConsentRequest(BaseModel):
    """Request model for withdrawing consent"""
    consent_type: str
    reason: Optional[str] = None


# Consent Text Templates (PDPL Compliant)
CONSENT_TEXTS = {
    "profiling": {
        "en": {
            "1.0": "I consent to the automated processing of my responses to generate a financial health score and related insights. This involves profiling under UAE PDPL Article 18. I understand that this processing will analyze my financial behavior patterns to provide personalized recommendations."
        },
        "ar": {
            "1.0": "أوافق على المعالجة التلقائية لردودي لإنشاء درجة صحة مالية ورؤى ذات صلة. يتضمن ذلك التنميط بموجب المادة 18 من قانون حماية البيانات الشخصية. أفهم أن هذه المعالجة ستحلل أنماط سلوكي المالي لتقديم توصيات مخصصة."
        }
    },
    "data_processing": {
        "en": {
            "1.0": "I consent to the collection, storage, and processing of my personal data as described in the Privacy Policy, including transfer to secure cloud infrastructure for service delivery. This consent covers data processing under UAE PDPL Article 5."
        },
        "ar": {
            "1.0": "أوافق على جمع وتخزين ومعالجة بياناتي الشخصية كما هو موضح في سياسة الخصوصية، بما في ذلك النقل إلى البنية التحتية السحابية الآمنة لتقديم الخدمة. تغطي هذه الموافقة معالجة البيانات بموجب المادة 5 من قانون حماية البيانات الشخصية."
        }
    },
    "marketing": {
        "en": {
            "1.0": "I consent to receive marketing communications about financial products, services, and educational content from National Bonds. I understand I can withdraw this consent at any time."
        },
        "ar": {
            "1.0": "أوافق على تلقي اتصالات تسويقية حول المنتجات المالية والخدمات والمحتوى التعليمي من صكوك الوطنية. أفهم أنه يمكنني سحب هذه الموافقة في أي وقت."
        }
    }
}


def get_consent_text(consent_type: str, language: str, version: str = "1.0") -> str:
    """Get the appropriate consent text"""
    try:
        return CONSENT_TEXTS[consent_type][language][version]
    except KeyError:
        return f"Consent text not found for {consent_type} in {language}"


def log_consent_action(
    db: Session,
    consent_id: int,
    user_id: Optional[int],
    session_id: str,
    action: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    description: Optional[str] = None
):
    """Create audit log entry for consent action"""
    audit_log = ConsentAuditLog(
        consent_id=consent_id,
        user_id=user_id,
        session_id=session_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        description=description
    )
    db.add(audit_log)
    db.commit()


@router.post("/grant", response_model=ConsentResponse)
async def grant_consent(
    request: Request,
    consent_data: ConsentGrantRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Grant consent for data processing activities (PDPL Article 18)
    
    This endpoint creates a PDPL-compliant consent record with:
    - Explicit consent text
    - Version tracking
    - Audit trail
    - IP address and user agent for verification
    """
    # Generate session ID if not provided
    session_id = consent_data.session_id or str(uuid.uuid4())
    
    # Get consent text
    consent_text = get_consent_text(
        consent_data.consent_type,
        consent_data.consent_language,
        consent_data.consent_version
    )
    
    # Get client information
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Check if there's an existing active consent
    existing_consent = db.query(UserConsent).filter(
        UserConsent.session_id == session_id,
        UserConsent.consent_type == consent_data.consent_type,
        UserConsent.is_active == True
    ).first()
    
    if existing_consent:
        # Update existing consent
        existing_consent.granted = True
        existing_consent.granted_at = datetime.utcnow()
        existing_consent.ip_address = ip_address
        existing_consent.user_agent = user_agent
        existing_consent.consent_version = consent_data.consent_version
        existing_consent.consent_text = consent_text
        existing_consent.updated_at = datetime.utcnow()
        
        if current_user:
            existing_consent.user_id = current_user.id
        
        db.commit()
        db.refresh(existing_consent)
        
        # Log action
        log_consent_action(
            db, existing_consent.id, 
            current_user.id if current_user else None,
            session_id, "updated", ip_address, user_agent,
            "Consent updated and re-granted"
        )
        
        return existing_consent
    
    # Create new consent record
    # PDPL Article 18: Consent expires after 2 years (can be adjusted)
    expires_at = datetime.utcnow() + timedelta(days=730)
    
    new_consent = UserConsent(
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        consent_type=consent_data.consent_type,
        granted=True,
        consent_version=consent_data.consent_version,
        consent_text=consent_text,
        consent_language=consent_data.consent_language,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        is_active=True,
        source_page=consent_data.source_page
    )
    
    db.add(new_consent)
    db.commit()
    db.refresh(new_consent)
    
    # Log action
    log_consent_action(
        db, new_consent.id,
        current_user.id if current_user else None,
        session_id, "granted", ip_address, user_agent,
        f"Consent granted for {consent_data.consent_type}"
    )
    
    return new_consent


@router.post("/withdraw/{consent_type}")
async def withdraw_consent(
    consent_type: str,
    request: Request,
    withdrawal_data: WithdrawConsentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Withdraw consent (PDPL Article 18.3 - Right to Withdraw)
    
    Users have the right to withdraw consent at any time.
    This will deactivate the consent and log the withdrawal.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required to withdraw consent")
    
    # Find active consent
    consent = db.query(UserConsent).filter(
        UserConsent.user_id == current_user.id,
        UserConsent.consent_type == consent_type,
        UserConsent.is_active == True
    ).first()
    
    if not consent:
        raise HTTPException(status_code=404, detail="No active consent found for this type")
    
    # Withdraw consent
    consent.is_active = False
    consent.granted = False
    consent.withdrawn_at = datetime.utcnow()
    consent.withdrawal_reason = withdrawal_data.reason
    consent.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log withdrawal
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    log_consent_action(
        db, consent.id, current_user.id,
        consent.session_id, "withdrawn", ip_address, user_agent,
        f"Consent withdrawn: {withdrawal_data.reason or 'No reason provided'}"
    )
    
    return {"message": "Consent successfully withdrawn", "consent_type": consent_type}


@router.get("/status", response_model=ConsentStatusResponse)
async def get_consent_status(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Check current consent status for a user or session
    
    Returns the status of all consent types and active consent records.
    """
    # Determine query filter
    if current_user:
        consents = db.query(UserConsent).filter(
            UserConsent.user_id == current_user.id,
            UserConsent.is_active == True
        ).all()
    elif session_id:
        consents = db.query(UserConsent).filter(
            UserConsent.session_id == session_id,
            UserConsent.is_active == True
        ).all()
    else:
        return ConsentStatusResponse(
            has_profiling_consent=False,
            has_data_processing_consent=False,
            has_marketing_consent=False,
            consents=[]
        )
    
    # Build response
    consent_dict = {c.consent_type: c for c in consents if c.granted}
    
    return ConsentStatusResponse(
        has_profiling_consent="profiling" in consent_dict,
        has_data_processing_consent="data_processing" in consent_dict,
        has_marketing_consent="marketing" in consent_dict,
        consents=[ConsentResponse.from_orm(c) for c in consents]
    )


@router.get("/history")
async def get_consent_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Get full consent history for a user (PDPL Article 13 - Right to Access)
    
    Returns all consent records and audit logs for the user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get all consents
    consents = db.query(UserConsent).filter(
        UserConsent.user_id == current_user.id
    ).order_by(UserConsent.created_at.desc()).all()
    
    # Get audit logs
    consent_ids = [c.id for c in consents]
    audit_logs = db.query(ConsentAuditLog).filter(
        ConsentAuditLog.consent_id.in_(consent_ids)
    ).order_by(ConsentAuditLog.action_timestamp.desc()).all()
    
    return {
        "consents": [ConsentResponse.from_orm(c) for c in consents],
        "audit_logs": [
            {
                "id": log.id,
                "consent_id": log.consent_id,
                "action": log.action,
                "timestamp": log.action_timestamp,
                "ip_address": log.ip_address,
                "description": log.description
            }
            for log in audit_logs
        ]
    }


@router.delete("/delete-all")
async def delete_all_consent_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Delete all consent records for a user (PDPL Article 15 - Right to Erasure)
    
    Note: In production, you may want to keep audit logs for compliance purposes
    even after user data deletion.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Delete consents
    deleted_count = db.query(UserConsent).filter(
        UserConsent.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "message": "All consent data deleted",
        "deleted_records": deleted_count
    }
