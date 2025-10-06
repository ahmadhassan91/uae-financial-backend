"""
Question Variation Service for managing alternative question versions.

This service handles the creation, validation, and management of question variations
while ensuring assessment consistency and scoring normalization.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import QuestionVariation, CustomerProfile, LocalizedContent
from app.surveys.question_definitions import (
    QuestionDefinition, LikertOption, FinancialFactor, 
    SURVEY_QUESTIONS_V2, question_lookup
)

logger = logging.getLogger(__name__)


@dataclass
class VariationValidationResult:
    """Result of question variation validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    consistency_score: float  # 0.0 to 1.0, how consistent with base question


@dataclass
class QuestionMappingResult:
    """Result of question variation mapping."""
    base_question_id: str
    variation_question_id: str
    mapping_confidence: float
    scoring_adjustment: Optional[float] = None


class QuestionVariationService:
    """
    Service for managing question variations and ensuring assessment consistency.
    
    This service provides functionality to create, validate, and manage question
    variations while maintaining the psychometric properties of the assessment.
    """
    
    def __init__(self, db: Session):
        """Initialize the service with database session."""
        self.db = db
        self._variation_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    def create_question_variation(
        self,
        base_question_id: str,
        variation_name: str,
        text: str,
        options: List[Dict[str, Any]],
        language: str = "en",
        demographic_rules: Optional[Dict[str, Any]] = None,
        company_ids: Optional[List[int]] = None
    ) -> Tuple[bool, str, Optional[QuestionVariation]]:
        """
        Create a new question variation.
        
        Args:
            base_question_id: ID of the base question
            variation_name: Name for this variation
            text: Question text
            options: List of option dictionaries with 'value' and 'label'
            language: Language code
            demographic_rules: Optional demographic targeting rules
            company_ids: Optional list of company IDs this applies to
            
        Returns:
            Tuple of (success, message, variation_object)
        """
        try:
            # Get base question
            base_question = question_lookup.get_question_by_id(base_question_id)
            if not base_question:
                return False, f"Base question '{base_question_id}' not found", None
            
            # Validate variation
            validation = self.validate_question_variation(
                base_question, text, options, language
            )
            
            if not validation.is_valid:
                return False, f"Validation failed: {'; '.join(validation.errors)}", None
            
            # Check for existing variation with same name
            existing = self.db.query(QuestionVariation).filter(
                and_(
                    QuestionVariation.base_question_id == base_question_id,
                    QuestionVariation.variation_name == variation_name,
                    QuestionVariation.language == language
                )
            ).first()
            
            if existing:
                return False, f"Variation '{variation_name}' already exists for this question", None
            
            # Create variation
            variation = QuestionVariation(
                base_question_id=base_question_id,
                variation_name=variation_name,
                language=language,
                text=text,
                options=options,
                demographic_rules=demographic_rules,
                company_ids=company_ids,
                factor=base_question.factor.value,
                weight=base_question.weight,
                is_active=True
            )
            
            self.db.add(variation)
            self.db.commit()
            self.db.refresh(variation)
            
            # Clear cache
            self._clear_cache()
            
            logger.info(
                f"Created question variation '{variation_name}' for '{base_question_id}'",
                extra={
                    'base_question_id': base_question_id,
                    'variation_name': variation_name,
                    'language': language
                }
            )
            
            return True, "Question variation created successfully", variation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating question variation: {str(e)}")
            return False, f"Error creating variation: {str(e)}", None
    
    def get_question_variations(
        self,
        base_question_id: Optional[str] = None,
        language: str = "en",
        company_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[QuestionVariation]:
        """
        Get question variations based on criteria.
        
        Args:
            base_question_id: Filter by base question ID
            language: Filter by language
            company_id: Filter by company ID
            active_only: Only return active variations
            
        Returns:
            List of matching question variations
        """
        try:
            query = self.db.query(QuestionVariation)
            
            if base_question_id:
                query = query.filter(QuestionVariation.base_question_id == base_question_id)
            
            if language:
                query = query.filter(QuestionVariation.language == language)
            
            if active_only:
                query = query.filter(QuestionVariation.is_active == True)
            
            if company_id:
                # Filter by company_ids JSON field
                query = query.filter(
                    QuestionVariation.company_ids.contains([company_id])
                )
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting question variations: {str(e)}")
            return []
    
    def get_best_variation_for_profile(
        self,
        base_question_id: str,
        profile: CustomerProfile,
        language: str = "en",
        company_id: Optional[int] = None
    ) -> Optional[QuestionVariation]:
        """
        Get the best question variation for a demographic profile.
        
        Args:
            base_question_id: Base question ID
            profile: Customer profile
            language: Language preference
            company_id: Optional company context
            
        Returns:
            Best matching question variation or None
        """
        try:
            # Get all variations for this question
            variations = self.get_question_variations(
                base_question_id=base_question_id,
                language=language,
                company_id=company_id
            )
            
            if not variations:
                return None
            
            # Score variations based on demographic match
            scored_variations = []
            for variation in variations:
                score = self._score_variation_for_profile(variation, profile, company_id)
                if score > 0:
                    scored_variations.append((variation, score))
            
            if not scored_variations:
                return None
            
            # Return highest scoring variation
            scored_variations.sort(key=lambda x: x[1], reverse=True)
            return scored_variations[0][0]
            
        except Exception as e:
            logger.error(f"Error getting best variation for profile: {str(e)}")
            return None
    
    def validate_question_variation(
        self,
        base_question: QuestionDefinition,
        variation_text: str,
        variation_options: List[Dict[str, Any]],
        language: str = "en"
    ) -> VariationValidationResult:
        """
        Validate a question variation for consistency with base question.
        
        Args:
            base_question: Base question definition
            variation_text: Variation question text
            variation_options: Variation options
            language: Language code
            
        Returns:
            Validation result with errors and consistency score
        """
        errors = []
        warnings = []
        consistency_score = 1.0
        
        try:
            # Validate basic structure
            if not variation_text or not variation_text.strip():
                errors.append("Question text cannot be empty")
            
            if not variation_options or not isinstance(variation_options, list):
                errors.append("Options must be a non-empty list")
            else:
                # Validate options structure
                if len(variation_options) != len(base_question.options):
                    errors.append(
                        f"Number of options ({len(variation_options)}) must match "
                        f"base question ({len(base_question.options)})"
                    )
                    consistency_score -= 0.3
                
                # Validate option values
                base_values = {opt.value for opt in base_question.options}
                variation_values = set()
                
                for i, option in enumerate(variation_options):
                    if not isinstance(option, dict):
                        errors.append(f"Option {i} must be a dictionary")
                        continue
                    
                    if 'value' not in option or 'label' not in option:
                        errors.append(f"Option {i} must have 'value' and 'label' fields")
                        continue
                    
                    try:
                        value = int(option['value'])
                        variation_values.add(value)
                    except (ValueError, TypeError):
                        errors.append(f"Option {i} value must be an integer")
                    
                    if not option['label'] or not isinstance(option['label'], str):
                        errors.append(f"Option {i} label must be a non-empty string")
                
                # Check value consistency
                if variation_values != base_values:
                    errors.append(
                        f"Option values {variation_values} must match "
                        f"base question values {base_values}"
                    )
                    consistency_score -= 0.4
            
            # Validate language-specific requirements
            if language == "ar":
                # Check for Arabic text
                if not self._contains_arabic_text(variation_text):
                    warnings.append("Arabic variation should contain Arabic text")
                    consistency_score -= 0.1
                
                # Check RTL considerations
                for option in variation_options:
                    if 'label' in option and not self._contains_arabic_text(option['label']):
                        warnings.append("Arabic option labels should contain Arabic text")
                        consistency_score -= 0.05
            
            # Semantic consistency check (basic)
            semantic_score = self._check_semantic_consistency(
                base_question.text, variation_text, language
            )
            consistency_score *= semantic_score
            
            if semantic_score < 0.7:
                warnings.append(
                    f"Low semantic consistency ({semantic_score:.2f}) with base question"
                )
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            consistency_score = 0.0
        
        return VariationValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            consistency_score=max(0.0, min(1.0, consistency_score))
        )
    
    def create_question_mapping(
        self,
        base_question_id: str,
        variation_question_id: str
    ) -> QuestionMappingResult:
        """
        Create a mapping between base question and variation for scoring.
        
        Args:
            base_question_id: Base question ID
            variation_question_id: Variation question ID (from QuestionVariation.id)
            
        Returns:
            Question mapping result with confidence score
        """
        try:
            # Get base question
            base_question = question_lookup.get_question_by_id(base_question_id)
            if not base_question:
                raise ValueError(f"Base question '{base_question_id}' not found")
            
            # Get variation
            variation = self.db.query(QuestionVariation).filter(
                QuestionVariation.id == int(variation_question_id)
            ).first()
            
            if not variation:
                raise ValueError(f"Question variation '{variation_question_id}' not found")
            
            # Validate mapping
            if variation.base_question_id != base_question_id:
                raise ValueError("Variation does not belong to the specified base question")
            
            # Calculate mapping confidence based on consistency
            validation = self.validate_question_variation(
                base_question,
                variation.text,
                variation.options
            )
            
            mapping_confidence = validation.consistency_score
            
            # Calculate scoring adjustment if needed
            scoring_adjustment = None
            if mapping_confidence < 0.9:
                # Apply small adjustment for lower consistency
                scoring_adjustment = (mapping_confidence - 1.0) * 0.1
            
            return QuestionMappingResult(
                base_question_id=base_question_id,
                variation_question_id=str(variation.id),
                mapping_confidence=mapping_confidence,
                scoring_adjustment=scoring_adjustment
            )
            
        except Exception as e:
            logger.error(f"Error creating question mapping: {str(e)}")
            raise
    
    def normalize_response_score(
        self,
        response_value: int,
        variation_id: int,
        base_question_id: str
    ) -> float:
        """
        Normalize a response score from a variation to base question scale.
        
        Args:
            response_value: Raw response value (1-5)
            variation_id: Question variation ID
            base_question_id: Base question ID
            
        Returns:
            Normalized score value
        """
        try:
            # Get mapping
            mapping = self.create_question_mapping(base_question_id, str(variation_id))
            
            # Apply scoring adjustment if needed
            normalized_score = float(response_value)
            
            if mapping.scoring_adjustment:
                normalized_score += mapping.scoring_adjustment
            
            # Ensure score stays within valid range
            normalized_score = max(1.0, min(5.0, normalized_score))
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error normalizing response score: {str(e)}")
            return float(response_value)  # Return original value on error
    
    def _score_variation_for_profile(
        self,
        variation: QuestionVariation,
        profile: CustomerProfile,
        company_id: Optional[int] = None
    ) -> float:
        """Score how well a variation matches a demographic profile."""
        score = 0.0
        
        try:
            # Company match
            if company_id and variation.company_ids:
                if company_id in variation.company_ids:
                    score += 50.0
                else:
                    return 0.0  # Company-specific variation doesn't match
            elif not variation.company_ids:
                score += 10.0  # General variation gets base score
            
            # Demographic rules match
            if variation.demographic_rules:
                from app.surveys.demographic_rule_engine import DemographicRuleEngine
                
                rule_engine = DemographicRuleEngine(self.db)
                context = rule_engine._profile_to_context(profile)
                
                if rule_engine._evaluate_conditions(variation.demographic_rules, context):
                    score += 40.0
                else:
                    return 0.0  # Demographic rules don't match
            else:
                score += 20.0  # No specific rules, general applicability
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring variation for profile: {str(e)}")
            return 0.0
    
    def _contains_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters."""
        if not text:
            return False
        
        # Arabic Unicode ranges
        arabic_ranges = [
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        ]
        
        for char in text:
            char_code = ord(char)
            for start, end in arabic_ranges:
                if start <= char_code <= end:
                    return True
        
        return False
    
    def _check_semantic_consistency(
        self,
        base_text: str,
        variation_text: str,
        language: str
    ) -> float:
        """
        Check semantic consistency between base and variation text.
        
        This is a simplified implementation. In production, you might want
        to use more sophisticated NLP techniques or translation services.
        """
        try:
            # Simple keyword-based consistency check
            base_words = set(base_text.lower().split())
            variation_words = set(variation_text.lower().split())
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                'my', 'i', 'me', 'you', 'your', 'it', 'its', 'we', 'our', 'they', 'their'
            }
            
            base_words -= stop_words
            variation_words -= stop_words
            
            if not base_words or not variation_words:
                return 0.5  # Neutral score if no meaningful words
            
            # Calculate Jaccard similarity
            intersection = len(base_words & variation_words)
            union = len(base_words | variation_words)
            
            if union == 0:
                return 0.5
            
            jaccard_similarity = intersection / union
            
            # For Arabic, we can't do meaningful word comparison, so return neutral
            if language == "ar":
                return 0.8  # Assume good consistency for Arabic
            
            # Boost score if key financial terms are preserved
            financial_terms = {
                'income', 'salary', 'money', 'budget', 'savings', 'debt', 'loan',
                'expenses', 'financial', 'planning', 'investment', 'retirement',
                'insurance', 'emergency', 'fund', 'credit', 'score'
            }
            
            base_financial = base_words & financial_terms
            variation_financial = variation_words & financial_terms
            
            if base_financial and variation_financial:
                financial_overlap = len(base_financial & variation_financial) / len(base_financial)
                jaccard_similarity = (jaccard_similarity + financial_overlap) / 2
            
            return min(1.0, jaccard_similarity + 0.2)  # Small boost for effort
            
        except Exception as e:
            logger.error(f"Error checking semantic consistency: {str(e)}")
            return 0.5  # Neutral score on error
    
    def _clear_cache(self):
        """Clear the variation cache."""
        self._variation_cache = {}
        self._cache_timestamp = None
    
    def update_variation_status(
        self,
        variation_id: int,
        is_active: bool
    ) -> Tuple[bool, str]:
        """
        Update the active status of a question variation.
        
        Args:
            variation_id: Question variation ID
            is_active: New active status
            
        Returns:
            Tuple of (success, message)
        """
        try:
            variation = self.db.query(QuestionVariation).filter(
                QuestionVariation.id == variation_id
            ).first()
            
            if not variation:
                return False, f"Question variation {variation_id} not found"
            
            variation.is_active = is_active
            variation.updated_at = datetime.utcnow()
            
            self.db.commit()
            self._clear_cache()
            
            status = "activated" if is_active else "deactivated"
            logger.info(f"Question variation {variation_id} {status}")
            
            return True, f"Question variation {status} successfully"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating variation status: {str(e)}")
            return False, f"Error updating variation: {str(e)}"
    
    def delete_variation(self, variation_id: int) -> Tuple[bool, str]:
        """
        Delete a question variation.
        
        Args:
            variation_id: Question variation ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            variation = self.db.query(QuestionVariation).filter(
                QuestionVariation.id == variation_id
            ).first()
            
            if not variation:
                return False, f"Question variation {variation_id} not found"
            
            # Check if variation is being used in any active surveys
            # This would require checking SurveyResponse.question_variations_used
            # For now, we'll just delete it
            
            self.db.delete(variation)
            self.db.commit()
            self._clear_cache()
            
            logger.info(f"Question variation {variation_id} deleted")
            
            return True, "Question variation deleted successfully"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting variation: {str(e)}")
            return False, f"Error deleting variation: {str(e)}"