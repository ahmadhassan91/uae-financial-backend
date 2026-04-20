from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import hashlib

from app.config import settings
from app.database import get_db
from app.models import CRMAPIKey, AuditLog, User
from app.auth.dependencies import get_current_full_admin_user
from app.crm.schemas import (
    CRMConsolidatedResponse, CRMRecord, CRMScores, CRMEngagement, 
    CRMActionPlans, CRMConsultation, CRMTimestamps, CRMMeta,
    CRMAPIKeyResponse, CRMAPIKeyCreate, CRMAPIKeyNew
)
from app.admin.services.consolidated_export import ConsolidatedExportService
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/crm", tags=["crm"])
security = HTTPBearer()

def get_crm_api_key(request: Request, db: Session = Depends(get_db), auth: HTTPAuthorizationCredentials = Security(security)):
    credentials = auth.credentials
    
    # 1. Check legacy fallback (from environment)
    if settings.CRM_API_KEY and credentials == settings.CRM_API_KEY:
        return "legacy_key"
    
    # 2. Check dynamic keys in database
    hashed_key = hashlib.sha256(credentials.encode()).hexdigest()
    db_key = db.query(CRMAPIKey).filter(
        CRMAPIKey.hashed_key == hashed_key,
        CRMAPIKey.is_active == True
    ).first()
    
    if not db_key:
        # Log failed attempt
        audit = AuditLog(
            action="CRM_ACCESS_FAILED",
            details={"reason": "Invalid API Key", "ip": request.client.host if request.client else "unknown"},
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CRM API Key"
        )
    
    return db_key.name

@router.get("/keys", response_model=List[CRMAPIKeyResponse])
async def list_crm_keys(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_full_admin_user)
):
    """List all CRM API keys (Masked)."""
    return db.query(CRMAPIKey).order_by(CRMAPIKey.created_at.desc()).all()

@router.post("/keys", response_model=CRMAPIKeyNew)
async def create_crm_key(
    data: CRMAPIKeyCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_full_admin_user)
):
    """Generate a new CRM API key."""
    plain_key = f"fc_{secrets.token_urlsafe(24)}"
    hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
    masked_key = f"{plain_key[:5]}...{plain_key[-4:]}"
    
    new_key = CRMAPIKey(
        name=data.name,
        masked_key=masked_key,
        hashed_key=hashed_key,
        is_active=True
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    # Audit log
    audit = AuditLog(
        action="CRM_KEY_CREATED",
        details={"name": data.name, "id": new_key.id, "created_by": admin.id}
    )
    db.add(audit)
    db.commit()
    
    # Attach plain_key so it's included in the response_model validation
    new_key.plain_key = plain_key
    return new_key

@router.patch("/keys/{key_id}/revoke", response_model=CRMAPIKeyResponse)
async def revoke_crm_key(
    key_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_full_admin_user)
):
    """Deactivate/Revoke a CRM API key."""
    db_key = db.query(CRMAPIKey).filter(CRMAPIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    db_key.is_active = False
    db_key.revoked_at = datetime.utcnow()
    db.commit()
    db.refresh(db_key)
    
    # Audit log
    audit = AuditLog(
        action="CRM_KEY_REVOKED",
        details={"name": db_key.name, "id": db_key.id, "revoked_by": admin.id}
    )
    db.add(audit)
    db.commit()
    
    return db_key

@router.get("/consolidated-data", response_model=CRMConsolidatedResponse)
@limiter.limit("60/hour")
async def get_consolidated_crm_data(
    request: Request,
    date_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key_name: str = Depends(get_crm_api_key)
):
    """
    Exposes consolidated survey data for CRM integration.
    Supports dynamic API keys and rate limiting (60/hour).
    """
    filters = {
        'date_range': date_range or 'today',
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Log successful access
    audit = AuditLog(
        action="CRM_ACCESS_SUCCESS",
        details={"key_name": api_key_name, "filters": filters}
    )
    db.add(audit)
    db.commit()
    
    service = ConsolidatedExportService(db)
    data_records = service.get_consolidated_data(filters)
    
    crm_records = []
    
    for record in data_records:
        if record['type'] in ["Submitted", "Lead"]:
            response = record['response_data']
            profile_data = record['profile_data']
            consultation = record['consultation_data']
            
            # Use service helpers for consistent formatting
            age = service._calculate_age(profile_data.get('date_of_birth', ''))
            mobile = profile_data.get('mobile_number', '')
            if mobile and not mobile.startswith('+'):
                mobile = '+971 ' + mobile

            # Formulate scores
            scores_data = CRMScores(
                total_score=round(response.total_score, 2) if response.total_score else 0.0,
                status_band=response.status_band or "",
                income_stream=service._get_category_score(response.category_scores, 'Income Stream'),
                savings_habit=service._get_category_score(response.category_scores, 'Savings Habit'),
                debt_management=service._get_category_score(response.category_scores, 'Debt Management'),
                retirement_planning=service._get_category_score(response.category_scores, 'Retirement Planning'),
                financial_protection=service._get_category_score(response.category_scores, 'Protecting Your Family'),
                financial_knowledge=service._get_category_score(response.category_scores, 'Emergency Savings')
            )

            # Formulate action plans
            insights = service._extract_insights(response.insights)
            action_plans = CRMActionPlans(
                plan_1=insights[0],
                plan_2=insights[1],
                plan_3=insights[2],
                plan_4=insights[3],
                plan_5=insights[4]
            )

            # Formulate engagement
            engagement = CRMEngagement(
                questions_answered=response.questions_answered or 0,
                total_questions=response.total_questions or 15,
                completion_percentage=100.0,
                leads_requested='Y' if response.leads_requested else 'N'
            )

            # Formulate consultation
            cons_data = None
            if consultation:
                cons_data = CRMConsultation(
                    status=consultation.status,
                    source=consultation.source,
                    preferred_method=consultation.preferred_contact_method,
                    preferred_time=consultation.preferred_time,
                    message=consultation.message,
                    notes=consultation.notes,
                    created_at=consultation.created_at,
                    contacted_at=consultation.contacted_at,
                    scheduled_at=consultation.scheduled_at
                )

            crm_records.append(CRMRecord(
                id=response.id,
                type=record['type'],
                name=profile_data.get('name', ''),
                email=profile_data.get('email', ''),
                mobile_number=mobile,
                age=age,
                gender=profile_data.get('gender', ''),
                nationality=profile_data.get('nationality', ''),
                emirate=profile_data.get('emirate', ''),
                children=str(profile_data.get('children', '')),
                employment_status=profile_data.get('employment_status', ''),
                income_range=profile_data.get('income_range', ''),
                company=profile_data.get('company_name', ''),
                unique_url=record['unique_url'],
                scores=scores_data,
                engagement=engagement,
                action_plans=action_plans,
                consultation=cons_data,
                timestamps=CRMTimestamps(submission_date=response.created_at)
            ))
            
        elif record['type'] == 'Incomplete':
            survey = record['survey_record']
            survey_responses = survey.responses or {}
            
            email = survey.email or survey_responses.get('email', '')
            phone = survey.phone_number or survey_responses.get('mobile_number', '')
            if phone and not phone.startswith('+'):
                phone = '+971 ' + phone

            completion_pct = 0
            if survey.total_steps > 0:
                completion_pct = round((survey.current_step / survey.total_steps) * 100, 1)

            crm_records.append(CRMRecord(
                id=record['id'],
                type='Incomplete',
                name=survey_responses.get('name', ''),
                email=email,
                mobile_number=phone,
                age=survey_responses.get('age', ''),
                gender=survey_responses.get('gender', ''),
                nationality=survey_responses.get('nationality', ''),
                emirate=survey_responses.get('emirate', ''),
                children=str(survey_responses.get('children', '')),
                employment_status=survey_responses.get('employment_status', ''),
                income_range=survey_responses.get('income_range', ''),
                company=survey.company.company_name if survey.company else '',
                unique_url=survey.company_url or (survey.company.unique_url if survey.company else ''),
                engagement=CRMEngagement(
                    questions_answered=survey.current_step,
                    total_questions=survey.total_steps,
                    completion_percentage=completion_pct,
                    leads_requested='N'
                ),
                timestamps=CRMTimestamps(submission_date=survey.created_at)
            ))

    return CRMConsolidatedResponse(
        meta=CRMMeta(
            total_count=len(crm_records),
            timestamp=datetime.utcnow()
        ),
        data=crm_records
    )
