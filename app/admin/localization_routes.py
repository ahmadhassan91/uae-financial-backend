"""
Admin API routes for localization content management.

This module provides REST API endpoints for managing localized content,
translation workflows, and quality assurance processes.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.database import get_db
from app.auth.dependencies import get_current_admin_user as get_admin_user
from app.models import User, LocalizedContent, AuditLog
from app.admin.schemas import (
    LocalizedContentCreate, LocalizedContentUpdate, LocalizedContentResponse,
    LocalizedContentListResponse, TranslationWorkflowRequest, TranslationWorkflowResponse,
    LocalizationAnalytics
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/localized-content", tags=["admin", "localization"])


@router.get("/", response_model=LocalizedContentListResponse)
async def list_localized_content(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    active_only: bool = Query(True, description="Only return active content"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    List localized content with filtering and pagination.
    """
    try:
        # Build query
        query = db.query(LocalizedContent)
        
        if content_type:
            query = query.filter(LocalizedContent.content_type == content_type)
        
        if language:
            query = query.filter(LocalizedContent.language == language)
        
        if active_only:
            query = query.filter(LocalizedContent.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        content_items = query.order_by(
            LocalizedContent.content_type.asc(),
            LocalizedContent.content_id.asc(),
            LocalizedContent.language.asc()
        ).offset(offset).limit(limit).all()
        
        # Convert to response format
        content_responses = []
        for item in content_items:
            content_response = LocalizedContentResponse(
                id=item.id,
                content_type=item.content_type,
                content_id=item.content_id,
                language=item.language,
                title=item.title,
                text=item.text,
                options=item.options,
                extra_data=item.extra_data,
                version=item.version,
                is_active=item.is_active,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            content_responses.append(content_response)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="list_localized_content",
            entity_type="localized_content",
            details={
                "filters": {
                    "content_type": content_type,
                    "language": language,
                    "active_only": active_only
                },
                "total_results": total
            }
        ))
        db.commit()
        
        return LocalizedContentListResponse(
            content=content_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error listing localized content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving localized content"
        )


@router.post("/", response_model=LocalizedContentResponse)
async def create_localized_content(
    content_data: LocalizedContentCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Create new localized content.
    """
    try:
        # Check for existing content with same type, id, and language
        existing = db.query(LocalizedContent).filter(
            and_(
                LocalizedContent.content_type == content_data.content_type,
                LocalizedContent.content_id == content_data.content_id,
                LocalizedContent.language == content_data.language
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Localized content already exists for {content_data.content_type}:{content_data.content_id} in {content_data.language}"
            )
        
        # Create content
        content = LocalizedContent(
            content_type=content_data.content_type,
            content_id=content_data.content_id,
            language=content_data.language,
            title=content_data.title,
            text=content_data.text,
            options=content_data.options,
            extra_data=content_data.extra_data,
            version=content_data.version,
            is_active=True
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="create_localized_content",
            entity_type="localized_content",
            entity_id=content.id,
            details={
                "content_type": content.content_type,
                "content_id": content.content_id,
                "language": content.language
            }
        ))
        db.commit()
        
        return LocalizedContentResponse(
            id=content.id,
            content_type=content.content_type,
            content_id=content.content_id,
            language=content.language,
            title=content.title,
            text=content.text,
            options=content.options,
            extra_data=content.extra_data,
            version=content.version,
            is_active=content.is_active,
            created_at=content.created_at,
            updated_at=content.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating localized content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating localized content"
        )


@router.get("/{content_id}", response_model=LocalizedContentResponse)
async def get_localized_content(
    content_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Get specific localized content by ID.
    """
    try:
        content = db.query(LocalizedContent).filter(
            LocalizedContent.id == content_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localized content not found"
            )
        
        return LocalizedContentResponse(
            id=content.id,
            content_type=content.content_type,
            content_id=content.content_id,
            language=content.language,
            title=content.title,
            text=content.text,
            options=content.options,
            extra_data=content.extra_data,
            version=content.version,
            is_active=content.is_active,
            created_at=content.created_at,
            updated_at=content.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting localized content {content_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving localized content"
        )


@router.put("/{content_id}", response_model=LocalizedContentResponse)
async def update_localized_content(
    content_id: int,
    content_data: LocalizedContentUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Update localized content.
    """
    try:
        content = db.query(LocalizedContent).filter(
            LocalizedContent.id == content_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localized content not found"
            )
        
        # Update fields
        if content_data.title is not None:
            content.title = content_data.title
        if content_data.text is not None:
            content.text = content_data.text
        if content_data.options is not None:
            content.options = content_data.options
        if content_data.extra_data is not None:
            content.extra_data = content_data.extra_data
        if content_data.version is not None:
            content.version = content_data.version
        if content_data.is_active is not None:
            content.is_active = content_data.is_active
        
        content.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(content)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="update_localized_content",
            entity_type="localized_content",
            entity_id=content.id,
            details={
                "updated_fields": [k for k, v in content_data.dict().items() if v is not None]
            }
        ))
        db.commit()
        
        return LocalizedContentResponse(
            id=content.id,
            content_type=content.content_type,
            content_id=content.content_id,
            language=content.language,
            title=content.title,
            text=content.text,
            options=content.options,
            extra_data=content.extra_data,
            version=content.version,
            is_active=content.is_active,
            created_at=content.created_at,
            updated_at=content.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating localized content {content_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating localized content"
        )


@router.delete("/{content_id}")
async def delete_localized_content(
    content_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Delete localized content.
    """
    try:
        content = db.query(LocalizedContent).filter(
            LocalizedContent.id == content_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localized content not found"
            )
        
        db.delete(content)
        db.commit()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="delete_localized_content",
            entity_type="localized_content",
            entity_id=content_id,
            details={
                "content_type": content.content_type,
                "content_id": content.content_id,
                "language": content.language
            }
        ))
        db.commit()
        
        return {"message": "Localized content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting localized content {content_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting localized content"
        )


@router.get("/analytics/overview", response_model=LocalizationAnalytics)
async def get_localization_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get analytics overview for localization.
    """
    try:
        # Total content items
        total_content_items = db.query(LocalizedContent).count()
        
        # Translated items (non-English content)
        translated_items = db.query(LocalizedContent).filter(
            LocalizedContent.language != "en"
        ).count()
        
        # Translation coverage by language
        language_stats = db.query(
            LocalizedContent.language,
            func.count(LocalizedContent.id).label('count')
        ).group_by(LocalizedContent.language).all()
        
        # Calculate coverage (assuming English is the base)
        english_count = next((count for lang, count in language_stats if lang == "en"), 0)
        translation_coverage = {}
        
        for language, count in language_stats:
            if language != "en" and english_count > 0:
                coverage = count / english_count
                translation_coverage[language] = min(1.0, coverage)
        
        # Pending translations (mock data - would need workflow tracking)
        pending_translations = max(0, english_count - translated_items)
        
        # Quality scores (mock data - would need quality assessment system)
        quality_scores = {
            "ar": 0.85,
            "overall": 0.85
        }
        
        # Most requested content (mock data - would need request tracking)
        most_requested_content = [
            {"content_type": "question", "content_id": "q1", "request_count": 25},
            {"content_type": "question", "content_id": "q2", "request_count": 20},
            {"content_type": "recommendation", "content_id": "rec_budgeting", "request_count": 18},
            {"content_type": "ui", "content_id": "welcome_message", "request_count": 15},
            {"content_type": "question", "content_id": "q3", "request_count": 12}
        ]
        
        return LocalizationAnalytics(
            total_content_items=total_content_items,
            translated_items=translated_items,
            translation_coverage=translation_coverage,
            pending_translations=pending_translations,
            quality_scores=quality_scores,
            most_requested_content=most_requested_content,
            analysis_period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting localization analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


# Translation Workflow Routes
workflow_router = APIRouter(prefix="/api/admin/translation-workflows", tags=["admin", "translation-workflows"])


@workflow_router.post("/", response_model=TranslationWorkflowResponse)
async def create_translation_workflow(
    workflow_data: TranslationWorkflowRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Create a new translation workflow.
    """
    try:
        workflow_id = str(uuid.uuid4())
        
        # Validate content IDs exist
        content_items = []
        for content_id in workflow_data.content_ids:
            # Check if source content exists
            source_content = db.query(LocalizedContent).filter(
                and_(
                    LocalizedContent.content_id == content_id,
                    LocalizedContent.language == workflow_data.source_language
                )
            ).first()
            
            if source_content:
                content_items.append({
                    "content_id": content_id,
                    "content_type": source_content.content_type,
                    "source_text": source_content.text,
                    "status": "pending"
                })
            else:
                # Create placeholder for missing source content
                content_items.append({
                    "content_id": content_id,
                    "content_type": "unknown",
                    "source_text": f"Source content not found for {content_id}",
                    "status": "error"
                })
        
        # Estimate completion time based on workflow type and content volume
        estimated_hours = len(content_items) * (2 if workflow_data.workflow_type == "manual" else 0.5)
        estimated_completion = datetime.now() + timedelta(hours=estimated_hours)
        
        # Mock workflow creation (in real implementation, this would integrate with translation service)
        workflow = TranslationWorkflowResponse(
            workflow_id=workflow_id,
            status="pending",
            content_items=content_items,
            estimated_completion=estimated_completion,
            assigned_translator=None,  # Would be assigned based on availability
            created_at=datetime.now()
        )
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="create_translation_workflow",
            entity_type="translation_workflow",
            details={
                "workflow_id": workflow_id,
                "content_count": len(content_items),
                "source_language": workflow_data.source_language,
                "target_language": workflow_data.target_language,
                "workflow_type": workflow_data.workflow_type
            }
        ))
        db.commit()
        
        return workflow
        
    except Exception as e:
        logger.error(f"Error creating translation workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating translation workflow"
        )


@workflow_router.get("/")
async def list_translation_workflows(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    List translation workflows.
    """
    try:
        # Mock workflow data (in real implementation, this would come from workflow service)
        workflows = [
            {
                "workflow_id": "wf-001",
                "status": "in_progress",
                "content_items": [
                    {"content_id": "q1", "content_type": "question", "source_text": "How stable is your income?", "status": "completed", "quality_score": 0.9},
                    {"content_id": "q2", "content_type": "question", "source_text": "Do you have multiple income sources?", "status": "in_progress"},
                    {"content_id": "q3", "content_type": "question", "source_text": "How often do you review your budget?", "status": "pending"}
                ],
                "estimated_completion": (datetime.now() + timedelta(hours=4)).isoformat(),
                "assigned_translator": "translator_001",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "workflow_id": "wf-002",
                "status": "completed",
                "content_items": [
                    {"content_id": "rec_budgeting", "content_type": "recommendation", "source_text": "Create a monthly budget", "status": "completed", "quality_score": 0.95},
                    {"content_id": "rec_savings", "content_type": "recommendation", "source_text": "Build an emergency fund", "status": "completed", "quality_score": 0.88}
                ],
                "estimated_completion": None,
                "assigned_translator": "translator_002",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        ]
        
        return {"workflows": workflows}
        
    except Exception as e:
        logger.error(f"Error listing translation workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving translation workflows"
        )


# Include workflow router
router.include_router(workflow_router)