"""API routes for localization management."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User, LocalizedContent
from app.localization.service import LocalizationService

router = APIRouter(prefix="/api/localization", tags=["localization"])


class LocalizedContentCreate(BaseModel):
    """Schema for creating localized content."""
    content_type: str = Field(..., description="Type of content (question, recommendation, ui)")
    content_id: str = Field(..., description="ID of the content to localize")
    language: str = Field(..., description="Language code (en, ar)")
    text: str = Field(..., description="Localized text content")
    title: Optional[str] = Field(None, description="Optional title")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Localized options for questions")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional localized data")
    version: str = Field("1.0", description="Content version")


class LocalizedContentUpdate(BaseModel):
    """Schema for updating localized content."""
    text: Optional[str] = Field(None, description="Updated text content")
    title: Optional[str] = Field(None, description="Updated title")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Updated options")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Updated extra data")
    is_active: Optional[bool] = Field(None, description="Active status")


class LocalizedContentResponse(BaseModel):
    """Schema for localized content response."""
    id: int
    content_type: str
    content_id: str
    language: str
    text: str
    title: Optional[str]
    options: Optional[List[Dict[str, Any]]]
    extra_data: Optional[Dict[str, Any]]
    version: str
    is_active: bool
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class ValidationResponse(BaseModel):
    """Schema for content validation response."""
    is_valid: bool
    warnings: List[str]
    errors: List[str]


@router.get("/languages", response_model=List[Dict[str, Any]])
async def get_supported_languages(
    db: Session = Depends(get_db)
):
    """Get list of supported languages."""
    service = LocalizationService(db)
    return await service.get_supported_languages()


@router.get("/content", response_model=List[LocalizedContentResponse])
async def get_localized_content(
    language: Optional[str] = None,
    content_type: Optional[str] = None,
    content_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get localized content with optional filtering."""
    try:
        query = db.query(LocalizedContent)
        
        if language:
            query = query.filter(LocalizedContent.language == language)
        if content_type:
            query = query.filter(LocalizedContent.content_type == content_type)
        if content_id:
            query = query.filter(LocalizedContent.content_id == content_id)
        
        content = query.order_by(
            LocalizedContent.content_type,
            LocalizedContent.content_id,
            LocalizedContent.language
        ).all()
        
        return content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving localized content: {str(e)}"
        )


@router.post("/content", response_model=LocalizedContentResponse)
async def create_localized_content(
    content_data: LocalizedContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new localized content."""
    try:
        service = LocalizationService(db)
        
        # Validate content first
        validation = await service.validate_content(
            content_data.content_type,
            content_data.content_id,
            content_data.language,
            content_data.text
        )
        
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content validation failed: {', '.join(validation['errors'])}"
            )
        
        # Create the content
        localized_content = await service.create_localized_content(
            content_type=content_data.content_type,
            content_id=content_data.content_id,
            language=content_data.language,
            text=content_data.text,
            title=content_data.title,
            options=content_data.options,
            extra_data=content_data.extra_data,
            version=content_data.version
        )
        
        return localized_content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating localized content: {str(e)}"
        )


@router.put("/content/{content_id}", response_model=LocalizedContentResponse)
async def update_localized_content(
    content_id: int,
    content_data: LocalizedContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing localized content."""
    try:
        service = LocalizationService(db)
        
        # Validate updated text if provided
        if content_data.text:
            existing_content = db.query(LocalizedContent).filter(
                LocalizedContent.id == content_id
            ).first()
            
            if not existing_content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Localized content not found"
                )
            
            validation = await service.validate_content(
                existing_content.content_type,
                existing_content.content_id,
                existing_content.language,
                content_data.text
            )
            
            if not validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Content validation failed: {', '.join(validation['errors'])}"
                )
        
        # Update the content
        updated_content = await service.update_localized_content(
            content_id=content_id,
            text=content_data.text,
            title=content_data.title,
            options=content_data.options,
            extra_data=content_data.extra_data,
            is_active=content_data.is_active
        )
        
        if not updated_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localized content not found"
            )
        
        return updated_content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating localized content: {str(e)}"
        )


@router.delete("/content/{content_id}")
async def delete_localized_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Soft delete localized content by setting is_active to False."""
    try:
        content = db.query(LocalizedContent).filter(
            LocalizedContent.id == content_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Localized content not found"
            )
        
        content.is_active = False
        db.commit()
        
        return {"message": "Localized content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting localized content: {str(e)}"
        )


@router.post("/content/validate", response_model=ValidationResponse)
async def validate_content(
    content_type: str,
    content_id: str,
    language: str,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Validate localized content before saving."""
    try:
        service = LocalizationService(db)
        validation_result = await service.validate_content(
            content_type, content_id, language, text
        )
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating content: {str(e)}"
        )


@router.get("/content/pending-approval", response_model=List[LocalizedContentResponse])
async def get_content_for_approval(
    language: str = "ar",
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get content that needs approval (for workflow management)."""
    try:
        service = LocalizationService(db)
        content = await service.get_content_for_approval(language, content_type)
        return content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content for approval: {str(e)}"
        )


@router.get("/questions/{language}", response_model=List[Dict[str, Any]])
async def get_questions_by_language(
    language: str,
    nationality: Optional[str] = None,
    age: Optional[int] = None,
    emirate: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get questions in the specified language with optional demographic filtering."""
    try:
        service = LocalizationService(db)
        
        # Build demographic profile if parameters provided
        demographic_profile = None
        if nationality or age or emirate:
            demographic_profile = {}
            if nationality:
                demographic_profile["nationality"] = nationality
            if age:
                demographic_profile["age"] = age
            if emirate:
                demographic_profile["emirate"] = emirate
        
        questions = await service.get_questions_by_language(
            language=language,
            demographic_profile=demographic_profile
        )
        
        return questions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving questions: {str(e)}"
        )


@router.get("/ui/{language}", response_model=Dict[str, str])
async def get_ui_translations(
    language: str,
    keys: Optional[str] = None,  # Comma-separated list of keys
    db: Session = Depends(get_db)
):
    """Get UI translations for the specified language."""
    try:
        service = LocalizationService(db)
        
        # Parse keys parameter
        content_keys = []
        if keys:
            content_keys = [key.strip() for key in keys.split(",")]
        else:
            # Get all available UI content keys for this language
            all_ui_content = db.query(LocalizedContent).filter(
                and_(
                    LocalizedContent.content_type == "ui",
                    LocalizedContent.language == language,
                    LocalizedContent.is_active == True
                )
            ).all()
            content_keys = [item.content_id for item in all_ui_content]
        
        translations = await service.get_ui_content_by_language(content_keys, language)
        return translations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving UI translations: {str(e)}"
        )


@router.post("/bulk-import")
async def bulk_import_translations(
    translations: Dict[str, Dict[str, Any]],
    language: str,
    content_type: str = "ui",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Bulk import translations from a dictionary."""
    try:
        service = LocalizationService(db)
        imported_count = 0
        errors = []
        
        for content_id, content_data in translations.items():
            try:
                text = content_data.get("text", "")
                title = content_data.get("title")
                options = content_data.get("options")
                extra_data = content_data.get("extra_data")
                
                if not text:
                    errors.append(f"Empty text for content_id: {content_id}")
                    continue
                
                await service.create_localized_content(
                    content_type=content_type,
                    content_id=content_id,
                    language=language,
                    text=text,
                    title=title,
                    options=options,
                    extra_data=extra_data
                )
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error importing {content_id}: {str(e)}")
        
        return {
            "imported_count": imported_count,
            "total_count": len(translations),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during bulk import: {str(e)}"
        )