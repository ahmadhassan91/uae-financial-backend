"""URL-based configuration service with caching."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import hashlib
from datetime import datetime, timedelta
import logging

from ..models import CompanyTracker, CompanyQuestionSet, CustomerProfile, QuestionVariation
from ..config import settings
from .question_manager import CompanyQuestionManager
from .cache_utils import get_cache_manager

logger = logging.getLogger(__name__)


class URLConfigurationService:
    """Manages URL-based configuration loading and caching."""
    
    def __init__(self, db: Session, cache_client=None):
        self.db = db
        self.cache_client = cache_client or get_cache_manager()
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.question_manager = CompanyQuestionManager(db)
    
    async def get_configuration_for_url(
        self,
        company_url: str,
        demographic_profile: Optional[CustomerProfile] = None,
        language: str = "en",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get complete configuration for a company URL."""
        
        # Generate cache key
        cache_key = self._generate_cache_key(company_url, demographic_profile, language)
        
        # Try to get from cache first
        if not force_refresh and self.cache_client:
            cached_config = await self._get_from_cache(cache_key)
            if cached_config:
                logger.info(f"Configuration cache hit for URL: {company_url}")
                return cached_config
        
        # Load configuration from database
        config = await self._load_configuration_from_db(
            company_url, demographic_profile, language
        )
        
        # Cache the configuration
        if self.cache_client:
            await self._set_cache(cache_key, config)
            logger.info(f"Configuration cached for URL: {company_url}")
        
        return config
    
    async def invalidate_cache_for_company(self, company_id: int):
        """Invalidate all cached configurations for a company."""
        if not self.cache_client:
            return
        
        # Get company URL
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.id == company_id
        ).first()
        
        if not company:
            return
        
        # Pattern to match all cache keys for this company
        pattern = f"url_config:{company.unique_url}:*"
        
        try:
            # Delete all matching keys
            keys = await self.cache_client.keys(pattern)
            if keys:
                await self.cache_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for company {company_id}")
        except Exception as e:
            logger.error(f"Error invalidating cache for company {company_id}: {e}")
    
    async def get_url_mapping(self, company_url: str) -> Optional[Dict[str, Any]]:
        """Get URL to configuration mapping."""
        
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url,
            CompanyTracker.is_active == True
        ).first()
        
        if not company:
            return None
        
        return {
            "company_id": company.id,
            "company_name": company.company_name,
            "url": company_url,
            "is_active": company.is_active,
            "has_custom_branding": bool(company.custom_branding),
            "has_custom_questions": bool(
                self.db.query(CompanyQuestionSet).filter(
                    CompanyQuestionSet.company_tracker_id == company.id,
                    CompanyQuestionSet.is_active == True
                ).first()
            ),
            "created_at": company.created_at.isoformat(),
            "last_updated": company.updated_at.isoformat() if company.updated_at else None
        }
    
    async def validate_configuration(
        self,
        company_url: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a configuration before applying it."""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if company exists
            company = self.db.query(CompanyTracker).filter(
                CompanyTracker.unique_url == company_url
            ).first()
            
            if not company:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Company not found for URL")
                return validation_result
            
            # Validate question set configuration
            if "question_set" in config_data:
                question_set_config = config_data["question_set"]
                
                # Validate base questions
                if "base_questions" in question_set_config:
                    from ..surveys.question_definitions import get_all_questions
                    all_questions = get_all_questions()
                    valid_question_ids = {q["id"] for q in all_questions}
                    
                    invalid_questions = set(question_set_config["base_questions"]) - valid_question_ids
                    if invalid_questions:
                        validation_result["errors"].append(
                            f"Invalid question IDs: {list(invalid_questions)}"
                        )
                
                # Validate question variations
                if "question_variations" in question_set_config:
                    for base_id, variation_name in question_set_config["question_variations"].items():
                        variation = self.db.query(QuestionVariation).filter(
                            QuestionVariation.base_question_id == base_id,
                            QuestionVariation.variation_name == variation_name,
                            QuestionVariation.is_active == True
                        ).first()
                        
                        if not variation:
                            validation_result["warnings"].append(
                                f"Variation '{variation_name}' not found for question '{base_id}'"
                            )
            
            # Validate branding configuration
            if "branding" in config_data:
                branding_config = config_data["branding"]
                
                # Check required branding fields
                if "logo_url" in branding_config:
                    # Could add URL validation here
                    pass
                
                if "colors" in branding_config:
                    colors = branding_config["colors"]
                    # Validate color format (hex colors)
                    for color_name, color_value in colors.items():
                        if not self._is_valid_hex_color(color_value):
                            validation_result["warnings"].append(
                                f"Invalid color format for {color_name}: {color_value}"
                            )
            
            # Validate demographic rules
            if "demographic_rules" in config_data:
                for rule in config_data["demographic_rules"]:
                    if not self._validate_demographic_rule_structure(rule):
                        validation_result["errors"].append(
                            f"Invalid demographic rule structure: {rule.get('name', 'unnamed')}"
                        )
            
            if validation_result["errors"]:
                validation_result["is_valid"] = False
        
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    async def apply_configuration_inheritance(
        self,
        company_config: Dict[str, Any],
        parent_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply configuration inheritance and overrides."""
        
        # Start with default configuration
        final_config = self._get_default_configuration()
        
        # Apply parent configuration if provided
        if parent_config:
            final_config = self._merge_configurations(final_config, parent_config)
        
        # Apply company-specific overrides
        final_config = self._merge_configurations(final_config, company_config)
        
        return final_config
    
    async def get_configuration_hierarchy(
        self,
        company_url: str
    ) -> Dict[str, Any]:
        """Get the configuration hierarchy for a company."""
        
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url
        ).first()
        
        if not company:
            return {"error": "Company not found"}
        
        # Get active question set
        question_set = self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.company_tracker_id == company.id,
            CompanyQuestionSet.is_active == True
        ).first()
        
        hierarchy = {
            "default_config": self._get_default_configuration(),
            "company_config": {
                "branding": company.custom_branding or {},
                "notification_settings": company.notification_settings or {},
                "localization_settings": getattr(company, 'localization_settings', {}) or {},
                "report_branding": getattr(company, 'report_branding', {}) or {}
            },
            "question_set_config": None,
            "final_config": None
        }
        
        if question_set:
            hierarchy["question_set_config"] = {
                "id": question_set.id,
                "name": question_set.name,
                "base_questions": question_set.base_questions,
                "custom_questions": question_set.custom_questions,
                "excluded_questions": question_set.excluded_questions,
                "question_variations": question_set.question_variations,
                "demographic_rules": question_set.demographic_rules
            }
        
        # Calculate final merged configuration
        hierarchy["final_config"] = await self.apply_configuration_inheritance(
            hierarchy["company_config"],
            hierarchy["question_set_config"]
        )
        
        return hierarchy
    
    def _generate_cache_key(
        self,
        company_url: str,
        demographic_profile: Optional[CustomerProfile],
        language: str
    ) -> str:
        """Generate a cache key for the configuration."""
        
        # Create a hash of the demographic profile
        profile_hash = "none"
        if demographic_profile:
            profile_data = {
                "nationality": demographic_profile.nationality,
                "age": demographic_profile.age,
                "emirate": demographic_profile.emirate,
                "employment_status": demographic_profile.employment_status,
                "monthly_income": demographic_profile.monthly_income
            }
            profile_str = json.dumps(profile_data, sort_keys=True)
            profile_hash = hashlib.md5(profile_str.encode()).hexdigest()[:8]
        
        return f"url_config:{company_url}:{language}:{profile_hash}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration from cache."""
        try:
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def _set_cache(self, cache_key: str, config: Dict[str, Any]):
        """Set configuration in cache."""
        try:
            await self.cache_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(config, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def _load_configuration_from_db(
        self,
        company_url: str,
        demographic_profile: Optional[CustomerProfile],
        language: str
    ) -> Dict[str, Any]:
        """Load configuration from database."""
        
        # Get company information
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url,
            CompanyTracker.is_active == True
        ).first()
        
        if not company:
            # Return default configuration for unknown URLs
            return {
                "company_config": None,
                "question_set": await self.question_manager._get_default_question_set(
                    demographic_profile, language
                ),
                "branding": {},
                "localization": {"language": language},
                "error": "Company not found"
            }
        
        # Get question set configuration
        question_set_config = await self.question_manager.get_company_question_set(
            company_url, demographic_profile, language
        )
        
        # Build complete configuration
        config = {
            "company_config": {
                "company_id": company.id,
                "company_name": company.company_name,
                "company_url": company_url,
                "is_active": company.is_active
            },
            "question_set": question_set_config,
            "branding": company.custom_branding or {},
            "notification_settings": company.notification_settings or {},
            "localization": {
                "language": language,
                "settings": getattr(company, 'localization_settings', {}) or {}
            },
            "report_branding": getattr(company, 'report_branding', {}) or {},
            "metadata": {
                "loaded_at": datetime.utcnow().isoformat(),
                "cache_ttl": self.cache_ttl,
                "demographic_profile_applied": demographic_profile is not None
            }
        }
        
        return config
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get the default system configuration."""
        return {
            "branding": {
                "primary_color": "#1e40af",
                "secondary_color": "#64748b",
                "logo_url": None,
                "company_name": "Financial Health Check"
            },
            "localization": {
                "language": "en",
                "rtl_support": False
            },
            "question_set": {
                "type": "default",
                "total_questions": 16
            },
            "features": {
                "email_reports": True,
                "pdf_reports": True,
                "arabic_support": True,
                "demographic_customization": True
            }
        }
    
    def _merge_configurations(
        self,
        base_config: Dict[str, Any],
        override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_configurations(merged[key], value)
            else:
                # Override the value
                merged[key] = value
        
        return merged
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not isinstance(color, str):
            return False
        
        if not color.startswith('#'):
            return False
        
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def _validate_demographic_rule_structure(self, rule: Dict[str, Any]) -> bool:
        """Validate demographic rule structure."""
        
        required_fields = ["name", "conditions", "actions"]
        
        # Check required fields
        for field in required_fields:
            if field not in rule:
                return False
        
        # Validate conditions structure
        conditions = rule["conditions"]
        if not isinstance(conditions, dict):
            return False
        
        # Validate actions structure
        actions = rule["actions"]
        if not isinstance(actions, dict):
            return False
        
        return True