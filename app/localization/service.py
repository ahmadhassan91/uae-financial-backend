"""Localization service for managing multi-language content."""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import LocalizedContent, QuestionVariation, DemographicRule
from app.surveys.question_definitions import SURVEY_QUESTIONS_V2
import json
import logging

logger = logging.getLogger(__name__)


class LocalizationService:
    """Service for managing localized content and translations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_questions_by_language(
        self, 
        language: str = "en",
        demographic_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get questions in the specified language with demographic filtering."""
        try:
            # Get base questions
            base_questions = SURVEY_QUESTIONS_V2
            localized_questions = []
            
            for question in base_questions:
                # Try to get localized version first
                localized = self.db.query(LocalizedContent).filter(
                    and_(
                        LocalizedContent.content_type == "question",
                        LocalizedContent.content_id == question.id,
                        LocalizedContent.language == language,
                        LocalizedContent.is_active == True
                    )
                ).first()
                
                if localized:
                    # Use localized content
                    localized_question = {
                        "id": question.id,
                        "text": localized.text,
                        "options": localized.options or [{"value": opt.value, "label": opt.label} for opt in question.options],
                        "factor": question.factor.value,
                        "weight": question.weight,
                        "language": language,
                        "title": localized.title,
                        "question_number": question.question_number,
                        "type": question.type,
                        "required": question.required,
                        "conditional": question.conditional
                    }
                else:
                    # Fall back to base question
                    localized_question = {
                        "id": question.id,
                        "text": question.text,
                        "options": [{"value": opt.value, "label": opt.label} for opt in question.options],
                        "factor": question.factor.value,
                        "weight": question.weight,
                        "language": language,
                        "question_number": question.question_number,
                        "type": question.type,
                        "required": question.required,
                        "conditional": question.conditional
                    }
                
                localized_questions.append(localized_question)
            
            # Apply demographic filtering if profile provided
            if demographic_profile:
                localized_questions = await self._apply_demographic_filtering(
                    localized_questions, demographic_profile, language
                )
            
            return localized_questions
            
        except Exception as e:
            logger.error(f"Error getting questions by language {language}: {str(e)}")
            # Fall back to base questions
            return [{
                "id": q.id,
                "text": q.text,
                "options": [{"value": opt.value, "label": opt.label} for opt in q.options],
                "factor": q.factor.value,
                "weight": q.weight,
                "language": language,
                "question_number": q.question_number,
                "type": q.type,
                "required": q.required,
                "conditional": q.conditional
            } for q in SURVEY_QUESTIONS_V2]
    
    async def get_recommendations_by_language(
        self,
        recommendations: List[Dict[str, Any]],
        language: str = "en",
        demographic_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get recommendations in the specified language."""
        try:
            localized_recommendations = []
            
            for rec in recommendations:
                # Try to get localized version
                localized = self.db.query(LocalizedContent).filter(
                    and_(
                        LocalizedContent.content_type == "recommendation",
                        LocalizedContent.content_id == rec.get("id", rec.get("category", "")),
                        LocalizedContent.language == language,
                        LocalizedContent.is_active == True
                    )
                ).first()
                
                if localized:
                    # Use localized content
                    localized_rec = {
                        **rec,
                        "title": localized.title or rec.get("title", ""),
                        "description": localized.text,
                        "language": language
                    }
                    
                    # Add localized action steps if available
                    if localized.extra_data and "action_steps" in localized.extra_data:
                        localized_rec["action_steps"] = localized.extra_data["action_steps"]
                else:
                    # Fall back to original recommendation
                    localized_rec = {
                        **rec,
                        "language": language
                    }
                
                # Apply cultural adaptations for Arabic
                if language == "ar" and demographic_profile:
                    localized_rec = await self._apply_cultural_adaptations(
                        localized_rec, demographic_profile
                    )
                
                localized_recommendations.append(localized_rec)
            
            return localized_recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations by language {language}: {str(e)}")
            return recommendations
    
    async def get_ui_content_by_language(
        self, 
        content_keys: List[str], 
        language: str = "en"
    ) -> Dict[str, str]:
        """Get UI content translations for the specified language."""
        try:
            translations = {}
            
            # Query all requested UI content at once
            localized_content = self.db.query(LocalizedContent).filter(
                and_(
                    LocalizedContent.content_type == "ui",
                    LocalizedContent.content_id.in_(content_keys),
                    LocalizedContent.language == language,
                    LocalizedContent.is_active == True
                )
            ).all()
            
            # Build translations dictionary
            for content in localized_content:
                translations[content.content_id] = content.text
            
            # Fill in missing translations with keys (fallback)
            for key in content_keys:
                if key not in translations:
                    translations[key] = key
            
            return translations
            
        except Exception as e:
            logger.error(f"Error getting UI content by language {language}: {str(e)}")
            # Return keys as fallback
            return {key: key for key in content_keys}
    
    async def create_localized_content(
        self,
        content_type: str,
        content_id: str,
        language: str,
        text: str,
        title: Optional[str] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        version: str = "1.0"
    ) -> LocalizedContent:
        """Create new localized content."""
        try:
            # Check if content already exists
            existing = self.db.query(LocalizedContent).filter(
                and_(
                    LocalizedContent.content_type == content_type,
                    LocalizedContent.content_id == content_id,
                    LocalizedContent.language == language
                )
            ).first()
            
            if existing:
                # Update existing content
                existing.text = text
                existing.title = title
                existing.options = options
                existing.extra_data = extra_data
                existing.version = version
                existing.is_active = True
                self.db.commit()
                return existing
            else:
                # Create new content
                localized_content = LocalizedContent(
                    content_type=content_type,
                    content_id=content_id,
                    language=language,
                    text=text,
                    title=title,
                    options=options,
                    extra_data=extra_data,
                    version=version,
                    is_active=True
                )
                
                self.db.add(localized_content)
                self.db.commit()
                self.db.refresh(localized_content)
                return localized_content
                
        except Exception as e:
            logger.error(f"Error creating localized content: {str(e)}")
            self.db.rollback()
            raise
    
    async def update_localized_content(
        self,
        content_id: int,
        text: Optional[str] = None,
        title: Optional[str] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[LocalizedContent]:
        """Update existing localized content."""
        try:
            content = self.db.query(LocalizedContent).filter(
                LocalizedContent.id == content_id
            ).first()
            
            if not content:
                return None
            
            # Update fields if provided
            if text is not None:
                content.text = text
            if title is not None:
                content.title = title
            if options is not None:
                content.options = options
            if extra_data is not None:
                content.extra_data = extra_data
            if is_active is not None:
                content.is_active = is_active
            
            self.db.commit()
            self.db.refresh(content)
            return content
            
        except Exception as e:
            logger.error(f"Error updating localized content {content_id}: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_content_for_approval(
        self, 
        language: str = "ar",
        content_type: Optional[str] = None
    ) -> List[LocalizedContent]:
        """Get content that needs approval (for workflow management)."""
        try:
            query = self.db.query(LocalizedContent).filter(
                LocalizedContent.language == language
            )
            
            if content_type:
                query = query.filter(LocalizedContent.content_type == content_type)
            
            # For now, return all content. In future, add approval status field
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting content for approval: {str(e)}")
            return []
    
    async def _apply_demographic_filtering(
        self,
        questions: List[Dict[str, Any]],
        demographic_profile: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:
        """Apply demographic rules to filter questions."""
        try:
            # Get active demographic rules
            rules = self.db.query(DemographicRule).filter(
                DemographicRule.is_active == True
            ).order_by(DemographicRule.priority).all()
            
            # Apply rules to determine question variations
            filtered_questions = []
            
            for question in questions:
                # Check if there are variations for this question
                variations = self.db.query(QuestionVariation).filter(
                    and_(
                        QuestionVariation.base_question_id == question["id"],
                        QuestionVariation.language == language,
                        QuestionVariation.is_active == True
                    )
                ).all()
                
                if variations:
                    # Find the best matching variation
                    best_variation = self._find_best_variation(
                        variations, demographic_profile
                    )
                    
                    if best_variation:
                        # Use the variation
                        question_data = {
                            "id": question["id"],
                            "text": best_variation.text,
                            "options": best_variation.options,
                            "factor": best_variation.factor,
                            "weight": best_variation.weight,
                            "language": language,
                            "variation_used": best_variation.variation_name,
                            "question_number": question.get("question_number", 0),
                            "type": question.get("type", "likert"),
                            "required": question.get("required", True),
                            "conditional": question.get("conditional", False)
                        }
                        filtered_questions.append(question_data)
                        continue
                
                # Use original question
                filtered_questions.append(question)
            
            return filtered_questions
            
        except Exception as e:
            logger.error(f"Error applying demographic filtering: {str(e)}")
            return questions
    
    def _find_best_variation(
        self,
        variations: List[QuestionVariation],
        demographic_profile: Dict[str, Any]
    ) -> Optional[QuestionVariation]:
        """Find the best matching question variation for the demographic profile."""
        try:
            for variation in variations:
                if not variation.demographic_rules:
                    continue
                
                # Evaluate demographic rules
                if self._evaluate_demographic_rules(
                    variation.demographic_rules, demographic_profile
                ):
                    return variation
            
            # Return first variation as fallback
            return variations[0] if variations else None
            
        except Exception as e:
            logger.error(f"Error finding best variation: {str(e)}")
            return variations[0] if variations else None
    
    def _evaluate_demographic_rules(
        self,
        rules: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> bool:
        """Evaluate demographic rules against a profile."""
        try:
            if "and" in rules:
                return all(
                    self._evaluate_demographic_rules(rule, profile)
                    for rule in rules["and"]
                )
            
            if "or" in rules:
                return any(
                    self._evaluate_demographic_rules(rule, profile)
                    for rule in rules["or"]
                )
            
            # Simple field comparison
            for field, condition in rules.items():
                profile_value = profile.get(field)
                
                if isinstance(condition, dict):
                    if "eq" in condition:
                        if profile_value != condition["eq"]:
                            return False
                    elif "in" in condition:
                        if profile_value not in condition["in"]:
                            return False
                    elif "gte" in condition:
                        if not profile_value or profile_value < condition["gte"]:
                            return False
                    elif "lte" in condition:
                        if not profile_value or profile_value > condition["lte"]:
                            return False
                else:
                    # Direct comparison
                    if profile_value != condition:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating demographic rules: {str(e)}")
            return False
    
    async def _apply_cultural_adaptations(
        self,
        recommendation: Dict[str, Any],
        demographic_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply cultural adaptations for Arabic recommendations."""
        try:
            # Add Islamic finance considerations for Muslim users
            if demographic_profile.get("islamic_finance_preference"):
                if "investment" in recommendation.get("category", "").lower():
                    # Add Sharia-compliant note
                    recommendation["cultural_note"] = "يُنصح بالتأكد من توافق الاستثمارات مع أحكام الشريعة الإسلامية"
            
            # Add UAE-specific context for citizens
            if demographic_profile.get("nationality") == "UAE":
                if "savings" in recommendation.get("category", "").lower():
                    recommendation["local_resources"] = [
                        "صندوق الادخار الإماراتي",
                        "برامج الادخار في البنوك المحلية"
                    ]
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error applying cultural adaptations: {str(e)}")
            return recommendation
    
    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages."""
        return [
            {"code": "en", "name": "English", "native_name": "English", "rtl": False},
            {"code": "ar", "name": "Arabic", "native_name": "العربية", "rtl": True}
        ]
    
    async def validate_content(
        self,
        content_type: str,
        content_id: str,
        language: str,
        text: str
    ) -> Dict[str, Any]:
        """Validate localized content for quality and consistency."""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            # Basic validation
            if not text or not text.strip():
                validation_result["errors"].append("Content text cannot be empty")
                validation_result["is_valid"] = False
            
            # Language-specific validation
            if language == "ar":
                # Check for Arabic characters
                if not any('\u0600' <= char <= '\u06FF' for char in text):
                    validation_result["warnings"].append(
                        "No Arabic characters detected in Arabic content"
                    )
                
                # Check for proper RTL markers if needed
                if content_type == "question" and len(text) > 50:
                    validation_result["warnings"].append(
                        "Consider adding RTL direction markers for long Arabic text"
                    )
            
            # Content type specific validation
            if content_type == "question":
                # Ensure question ends with question mark
                if not text.strip().endswith(('?', '؟')):
                    validation_result["warnings"].append(
                        "Question should end with a question mark"
                    )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }