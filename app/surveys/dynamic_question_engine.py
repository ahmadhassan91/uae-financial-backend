"""
Dynamic Question Engine for profile-based question selection.

This engine combines demographic rule evaluation, question variation management,
and caching to provide optimized question selection for different user profiles.
"""
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Session
from app.models import CustomerProfile, CompanyTracker, QuestionVariation
from app.surveys.question_definitions import (
    QuestionDefinition, LikertOption, FinancialFactor,
    SURVEY_QUESTIONS_V2, question_lookup
)
from app.surveys.demographic_rule_engine import (
    DemographicRuleEngine, QuestionSelectionResult
)
from app.surveys.question_variation_service import QuestionVariationService

logger = logging.getLogger(__name__)


class QuestionSelectionStrategy(str, Enum):
    """Strategies for question selection."""
    DEFAULT = "default"           # Use base questions
    DEMOGRAPHIC = "demographic"   # Apply demographic rules
    COMPANY = "company"          # Use company-specific questions
    HYBRID = "hybrid"            # Combine demographic and company rules


@dataclass
class DynamicQuestionSet:
    """Result of dynamic question selection."""
    questions: List[QuestionDefinition]
    variations_used: Dict[str, int]  # question_id -> variation_id
    selection_metadata: Dict[str, Any]
    cache_key: str
    generated_at: datetime
    strategy_used: QuestionSelectionStrategy


@dataclass
class QuestionAnalytics:
    """Analytics data for question selection."""
    total_selections: int
    demographic_matches: int
    company_matches: int
    variation_usage: Dict[str, int]
    cache_hit_rate: float
    average_selection_time: float


class DynamicQuestionEngine:
    """
    Engine for dynamic question selection based on demographic profiles and company settings.
    
    This engine provides intelligent question selection with caching, analytics,
    and A/B testing capabilities.
    """
    
    def __init__(self, db: Session, redis_client=None):
        """
        Initialize the dynamic question engine.
        
        Args:
            db: Database session
            redis_client: Optional Redis client for caching
        """
        self.db = db
        self.redis = redis_client
        self.rule_engine = DemographicRuleEngine(db)
        self.variation_service = QuestionVariationService(db)
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour
        self.cache_prefix = "dynamic_questions:"
        
        # Analytics tracking
        self._analytics = {
            'total_selections': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'selection_times': []
        }
    
    async def get_questions_for_profile(
        self,
        profile: CustomerProfile,
        company_id: Optional[int] = None,
        language: str = "en",
        strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.HYBRID,
        force_refresh: bool = False
    ) -> DynamicQuestionSet:
        """
        Get optimized question set for a demographic profile.
        
        Args:
            profile: Customer demographic profile
            company_id: Optional company context
            language: Language preference
            strategy: Question selection strategy
            force_refresh: Force cache refresh
            
        Returns:
            Dynamic question set with selected questions and metadata
        """
        start_time = datetime.now()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(profile, company_id, language, strategy)
            
            # Try cache first (unless force refresh)
            if not force_refresh:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    self._analytics['cache_hits'] += 1
                    self._analytics['total_selections'] += 1
                    return cached_result
            
            self._analytics['cache_misses'] += 1
            
            # Generate question set based on strategy
            if strategy == QuestionSelectionStrategy.DEFAULT:
                question_set = await self._get_default_questions(language)
            elif strategy == QuestionSelectionStrategy.DEMOGRAPHIC:
                question_set = await self._get_demographic_questions(profile, language)
            elif strategy == QuestionSelectionStrategy.COMPANY:
                question_set = await self._get_company_questions(profile, company_id, language)
            else:  # HYBRID
                question_set = await self._get_hybrid_questions(profile, company_id, language)
            
            # Cache the result
            await self._cache_result(cache_key, question_set)
            
            # Update analytics
            selection_time = (datetime.now() - start_time).total_seconds()
            self._analytics['selection_times'].append(selection_time)
            self._analytics['total_selections'] += 1
            
            logger.info(
                f"Generated question set for profile {profile.id}",
                extra={
                    'profile_id': profile.id,
                    'company_id': company_id,
                    'strategy': strategy,
                    'question_count': len(question_set.questions),
                    'variations_count': len(question_set.variations_used),
                    'selection_time': selection_time
                }
            )
            
            return question_set
            
        except Exception as e:
            logger.error(f"Error generating questions for profile {profile.id}: {str(e)}")
            # Fallback to default questions
            return await self._get_default_questions(language)
    
    async def _get_default_questions(self, language: str = "en") -> DynamicQuestionSet:
        """Get default question set without any customization."""
        questions = []
        variations_used = {}
        
        for base_question in SURVEY_QUESTIONS_V2:
            # Convert to QuestionDefinition with localization if needed
            if language != "en":
                localized_question = await self._localize_question(base_question, language)
                questions.append(localized_question)
            else:
                questions.append(base_question)
        
        return DynamicQuestionSet(
            questions=questions,
            variations_used=variations_used,
            selection_metadata={
                'strategy': QuestionSelectionStrategy.DEFAULT,
                'language': language,
                'total_questions': len(questions)
            },
            cache_key="",
            generated_at=datetime.now(),
            strategy_used=QuestionSelectionStrategy.DEFAULT
        )
    
    async def _get_demographic_questions(
        self,
        profile: CustomerProfile,
        language: str = "en"
    ) -> DynamicQuestionSet:
        """Get questions based on demographic rules."""
        # Use rule engine to select questions
        selection_result = self.rule_engine.select_questions_for_profile(profile)
        
        questions = []
        variations_used = {}
        
        # If no questions selected by rules, fall back to base questions
        question_ids = selection_result.selected_questions
        if not question_ids:
            question_ids = question_lookup.get_all_question_ids()
        
        for question_id in question_ids:
            # Try to get best variation for this profile
            variation = self.variation_service.get_best_variation_for_profile(
                question_id, profile, language
            )
            
            if variation:
                # Use variation
                question_def = self._variation_to_question_definition(variation)
                questions.append(question_def)
                variations_used[question_id] = variation.id
            else:
                # Use base question
                base_question = question_lookup.get_question_by_id(question_id)
                if base_question:
                    if language != "en":
                        localized_question = await self._localize_question(base_question, language)
                        questions.append(localized_question)
                    else:
                        questions.append(base_question)
        
        return DynamicQuestionSet(
            questions=questions,
            variations_used=variations_used,
            selection_metadata={
                'strategy': QuestionSelectionStrategy.DEMOGRAPHIC,
                'language': language,
                'applied_rules': [r.rule_name for r in selection_result.applied_rules if r.matched],
                'excluded_questions': selection_result.excluded_questions,
                'added_questions': selection_result.added_questions,
                'profile_hash': selection_result.demographic_profile_hash
            },
            cache_key="",
            generated_at=datetime.now(),
            strategy_used=QuestionSelectionStrategy.DEMOGRAPHIC
        )
    
    async def _get_company_questions(
        self,
        profile: CustomerProfile,
        company_id: Optional[int],
        language: str = "en"
    ) -> DynamicQuestionSet:
        """Get questions based on company configuration."""
        if not company_id:
            return await self._get_default_questions(language)
        
        # Get company configuration
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.id == company_id
        ).first()
        
        if not company or not company.question_set_config:
            return await self._get_default_questions(language)
        
        questions = []
        variations_used = {}
        
        try:
            config = company.question_set_config
            if isinstance(config, str):
                config = json.loads(config)
            
            # Get base questions from config
            base_questions = config.get('base_questions', question_lookup.get_all_question_ids())
            
            for question_id in base_questions:
                # Check for company-specific variations
                variations = self.variation_service.get_question_variations(
                    base_question_id=question_id,
                    language=language,
                    company_id=company_id
                )
                
                if variations:
                    # Use first matching variation
                    variation = variations[0]
                    question_def = self._variation_to_question_definition(variation)
                    questions.append(question_def)
                    variations_used[question_id] = variation.id
                else:
                    # Use base question
                    base_question = question_lookup.get_question_by_id(question_id)
                    if base_question:
                        if language != "en":
                            localized_question = await self._localize_question(base_question, language)
                            questions.append(localized_question)
                        else:
                            questions.append(base_question)
            
        except Exception as e:
            logger.error(f"Error processing company question config: {str(e)}")
            return await self._get_default_questions(language)
        
        return DynamicQuestionSet(
            questions=questions,
            variations_used=variations_used,
            selection_metadata={
                'strategy': QuestionSelectionStrategy.COMPANY,
                'language': language,
                'company_id': company_id,
                'company_name': company.company_name,
                'total_questions': len(questions)
            },
            cache_key="",
            generated_at=datetime.now(),
            strategy_used=QuestionSelectionStrategy.COMPANY
        )
    
    async def _get_hybrid_questions(
        self,
        profile: CustomerProfile,
        company_id: Optional[int],
        language: str = "en"
    ) -> DynamicQuestionSet:
        """Get questions using hybrid approach (demographic + company rules)."""
        # Start with demographic selection
        demographic_result = await self._get_demographic_questions(profile, language)
        
        if not company_id:
            return demographic_result
        
        # Apply company-specific overrides
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.id == company_id
        ).first()
        
        if not company:
            return demographic_result
        
        questions = demographic_result.questions.copy()
        variations_used = demographic_result.variations_used.copy()
        
        # Apply company-specific variations where available
        for i, question in enumerate(questions):
            company_variations = self.variation_service.get_question_variations(
                base_question_id=question.id,
                language=language,
                company_id=company_id
            )
            
            if company_variations:
                # Use company-specific variation
                variation = company_variations[0]
                questions[i] = self._variation_to_question_definition(variation)
                variations_used[question.id] = variation.id
        
        # Merge metadata
        metadata = demographic_result.selection_metadata.copy()
        metadata.update({
            'strategy': QuestionSelectionStrategy.HYBRID,
            'company_id': company_id,
            'company_name': company.company_name,
            'company_variations_applied': len([v for v in variations_used.values() if v])
        })
        
        return DynamicQuestionSet(
            questions=questions,
            variations_used=variations_used,
            selection_metadata=metadata,
            cache_key="",
            generated_at=datetime.now(),
            strategy_used=QuestionSelectionStrategy.HYBRID
        )
    
    def _variation_to_question_definition(self, variation: QuestionVariation) -> QuestionDefinition:
        """Convert QuestionVariation to QuestionDefinition."""
        # Get base question for metadata
        base_question = question_lookup.get_question_by_id(variation.base_question_id)
        
        if not base_question:
            raise ValueError(f"Base question {variation.base_question_id} not found")
        
        # Convert options
        options = []
        for opt in variation.options:
            options.append(LikertOption(
                value=opt['value'],
                label=opt['label']
            ))
        
        return QuestionDefinition(
            id=variation.base_question_id,  # Keep base ID for scoring
            question_number=base_question.question_number,
            text=variation.text,
            type=base_question.type,
            options=options,
            required=base_question.required,
            factor=FinancialFactor(variation.factor),
            weight=variation.weight,
            conditional=base_question.conditional
        )
    
    async def _localize_question(
        self,
        question: QuestionDefinition,
        language: str
    ) -> QuestionDefinition:
        """Localize a question to the specified language."""
        # This would integrate with the localization service
        # For now, return the original question
        # TODO: Implement proper localization lookup
        return question
    
    def _generate_cache_key(
        self,
        profile: CustomerProfile,
        company_id: Optional[int],
        language: str,
        strategy: QuestionSelectionStrategy
    ) -> str:
        """Generate cache key for question selection."""
        # Create profile hash
        profile_data = {
            'age': profile.age,
            'nationality': profile.nationality,
            'emirate': profile.emirate,
            'employment_status': profile.employment_status,
            'monthly_income': profile.monthly_income,
            'education_level': getattr(profile, 'education_level', None),
            'years_in_uae': getattr(profile, 'years_in_uae', None),
            'islamic_finance_preference': getattr(profile, 'islamic_finance_preference', False)
        }
        
        # Remove None values
        profile_data = {k: v for k, v in profile_data.items() if v is not None}
        
        # Create hash
        profile_str = json.dumps(profile_data, sort_keys=True)
        profile_hash = hashlib.md5(profile_str.encode()).hexdigest()[:8]
        
        # Combine with other parameters
        key_parts = [
            self.cache_prefix,
            profile_hash,
            str(company_id) if company_id else "no_company",
            language,
            strategy.value
        ]
        
        return ":".join(key_parts)
    
    async def _get_from_cache(self, cache_key: str) -> Optional[DynamicQuestionSet]:
        """Get question set from cache."""
        if not self.redis:
            return None
        
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                
                # Check if cache is still valid
                generated_at = datetime.fromisoformat(data['generated_at'])
                if datetime.now() - generated_at > timedelta(seconds=self.cache_ttl):
                    await self.redis.delete(cache_key)
                    return None
                
                # Reconstruct question set
                questions = []
                for q_data in data['questions']:
                    options = [LikertOption(**opt) for opt in q_data['options']]
                    question = QuestionDefinition(
                        id=q_data['id'],
                        question_number=q_data['question_number'],
                        text=q_data['text'],
                        type=q_data['type'],
                        options=options,
                        required=q_data['required'],
                        factor=FinancialFactor(q_data['factor']),
                        weight=q_data['weight'],
                        conditional=q_data.get('conditional', False)
                    )
                    questions.append(question)
                
                return DynamicQuestionSet(
                    questions=questions,
                    variations_used=data['variations_used'],
                    selection_metadata=data['selection_metadata'],
                    cache_key=cache_key,
                    generated_at=generated_at,
                    strategy_used=QuestionSelectionStrategy(data['strategy_used'])
                )
                
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def _cache_result(self, cache_key: str, question_set: DynamicQuestionSet):
        """Cache question set result."""
        if not self.redis:
            return
        
        try:
            # Serialize question set
            questions_data = []
            for q in question_set.questions:
                options_data = [{'value': opt.value, 'label': opt.label} for opt in q.options]
                questions_data.append({
                    'id': q.id,
                    'question_number': q.question_number,
                    'text': q.text,
                    'type': q.type,
                    'options': options_data,
                    'required': q.required,
                    'factor': q.factor.value,
                    'weight': q.weight,
                    'conditional': q.conditional
                })
            
            cache_data = {
                'questions': questions_data,
                'variations_used': question_set.variations_used,
                'selection_metadata': question_set.selection_metadata,
                'generated_at': question_set.generated_at.isoformat(),
                'strategy_used': question_set.strategy_used.value
            }
            
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
    
    def get_analytics(self) -> QuestionAnalytics:
        """Get analytics data for question selection."""
        total_requests = self._analytics['total_selections']
        cache_hits = self._analytics['cache_hits']
        
        cache_hit_rate = (cache_hits / total_requests) if total_requests > 0 else 0.0
        
        selection_times = self._analytics['selection_times']
        avg_selection_time = sum(selection_times) / len(selection_times) if selection_times else 0.0
        
        return QuestionAnalytics(
            total_selections=total_requests,
            demographic_matches=0,  # TODO: Track this
            company_matches=0,      # TODO: Track this
            variation_usage={},     # TODO: Track this
            cache_hit_rate=cache_hit_rate,
            average_selection_time=avg_selection_time
        )
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """Clear question selection cache."""
        if not self.redis:
            return
        
        try:
            if pattern:
                keys = await self.redis.keys(f"{self.cache_prefix}{pattern}")
            else:
                keys = await self.redis.keys(f"{self.cache_prefix}*")
            
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    def reset_analytics(self):
        """Reset analytics counters."""
        self._analytics = {
            'total_selections': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'selection_times': []
        }