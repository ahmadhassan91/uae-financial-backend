"""
Demographic Rule Engine for dynamic question selection based on user demographics.

This module implements a flexible rule engine that evaluates demographic conditions
and applies appropriate question variations while maintaining assessment validity.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from sqlalchemy.orm import Session
from app.models import DemographicRule, CustomerProfile, QuestionVariation
from app.surveys.question_definitions import QuestionDefinition, SURVEY_QUESTIONS_V2, question_lookup

logger = logging.getLogger(__name__)


class RuleOperator(str, Enum):
    """Supported operators for demographic rule conditions."""
    EQ = "eq"           # equals
    NE = "ne"           # not equals
    GT = "gt"           # greater than
    GTE = "gte"         # greater than or equal
    LT = "lt"           # less than
    LTE = "lte"         # less than or equal
    IN = "in"           # in list
    NOT_IN = "not_in"   # not in list
    CONTAINS = "contains"  # string contains
    STARTS_WITH = "starts_with"  # string starts with
    ENDS_WITH = "ends_with"      # string ends with


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation."""
    rule_id: int
    rule_name: str
    matched: bool
    actions: Dict[str, Any]
    priority: int
    evaluation_details: Optional[Dict[str, Any]] = None


@dataclass
class QuestionSelectionResult:
    """Result of question selection process."""
    selected_questions: List[str]
    excluded_questions: List[str]
    added_questions: List[str]
    applied_rules: List[RuleEvaluationResult]
    demographic_profile_hash: str


class DemographicRuleEngine:
    """
    Engine for evaluating demographic rules and selecting appropriate questions.
    
    Supports complex rule conditions with logical operators and maintains
    audit trails for compliance and debugging.
    """
    
    # Protected demographic fields that require special validation
    PROTECTED_FIELDS = {
        'gender', 'nationality', 'religion', 'race', 'ethnicity'
    }
    
    # Allowed demographic fields for rule evaluation
    ALLOWED_FIELDS = {
        'age', 'nationality', 'emirate', 'employment_status', 'monthly_income',
        'education_level', 'years_in_uae', 'family_status', 'housing_status',
        'banking_relationship', 'investment_experience', 'islamic_finance_preference',
        'household_size', 'children', 'industry', 'position'
    }
    
    def __init__(self, db: Session):
        """Initialize the rule engine with database session."""
        self.db = db
        self._rule_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    def evaluate_rules_for_profile(
        self, 
        profile: CustomerProfile,
        company_id: Optional[int] = None
    ) -> List[RuleEvaluationResult]:
        """
        Evaluate all applicable demographic rules for a user profile.
        
        Args:
            profile: Customer profile with demographic data
            company_id: Optional company ID for company-specific rules
            
        Returns:
            List of rule evaluation results sorted by priority
        """
        try:
            # Get applicable rules
            rules = self._get_applicable_rules(company_id)
            
            # Convert profile to evaluation context
            context = self._profile_to_context(profile)
            
            # Evaluate each rule
            results = []
            for rule in rules:
                try:
                    result = self._evaluate_single_rule(rule, context)
                    results.append(result)
                    
                    if result.matched:
                        logger.info(
                            f"Rule '{rule.name}' matched for profile {profile.id}",
                            extra={
                                'rule_id': rule.id,
                                'profile_id': profile.id,
                                'actions': result.actions
                            }
                        )
                except Exception as e:
                    logger.error(
                        f"Error evaluating rule {rule.id} '{rule.name}': {str(e)}",
                        extra={'rule_id': rule.id, 'profile_id': profile.id}
                    )
                    continue
            
            # Sort by priority (lower number = higher priority)
            results.sort(key=lambda x: x.priority)
            
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating rules for profile {profile.id}: {str(e)}")
            return []
    
    def select_questions_for_profile(
        self,
        profile: CustomerProfile,
        base_questions: Optional[List[str]] = None,
        company_id: Optional[int] = None
    ) -> QuestionSelectionResult:
        """
        Select appropriate questions for a demographic profile.
        
        Args:
            profile: Customer profile with demographic data
            base_questions: Base question IDs to start with (defaults to all questions)
            company_id: Optional company ID for company-specific rules
            
        Returns:
            Question selection result with applied rules and final question list
        """
        if base_questions is None:
            base_questions = question_lookup.get_all_question_ids()
        
        # Evaluate rules
        rule_results = self.evaluate_rules_for_profile(profile, company_id)
        
        # Apply rule actions
        selected_questions = set(base_questions)
        excluded_questions = set()
        added_questions = set()
        
        for result in rule_results:
            if not result.matched:
                continue
                
            actions = result.actions
            
            # Handle include_questions (these are variations, not replacements)
            # We keep the base questions and just note which variations to use
            if 'include_questions' in actions:
                include_list = actions['include_questions']
                if isinstance(include_list, list):
                    # These are variation names, not question replacements
                    # The actual variation selection happens in the question engine
                    pass
            
            # Handle exclude_questions
            if 'exclude_questions' in actions:
                exclude_list = actions['exclude_questions']
                if isinstance(exclude_list, list):
                    for q_id in exclude_list:
                        if q_id in selected_questions:
                            selected_questions.remove(q_id)
                            excluded_questions.add(q_id)
            
            # Handle add_questions (these are additional questions)
            if 'add_questions' in actions:
                add_list = actions['add_questions']
                if isinstance(add_list, list):
                    for q_id in add_list:
                        if q_id not in selected_questions:
                            selected_questions.add(q_id)
                            added_questions.add(q_id)
        
        # Generate profile hash for caching
        profile_hash = self._generate_profile_hash(profile)
        
        return QuestionSelectionResult(
            selected_questions=list(selected_questions),
            excluded_questions=list(excluded_questions),
            added_questions=list(added_questions),
            applied_rules=rule_results,
            demographic_profile_hash=profile_hash
        )
    
    def validate_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a demographic rule for compliance and correctness.
        
        Args:
            rule_data: Rule data dictionary with conditions and actions
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        try:
            # Validate conditions
            if 'conditions' not in rule_data:
                errors.append("Rule must have 'conditions' field")
            else:
                condition_errors = self._validate_conditions(rule_data['conditions'])
                errors.extend(condition_errors)
            
            # Validate actions
            if 'actions' not in rule_data:
                errors.append("Rule must have 'actions' field")
            else:
                action_errors = self._validate_actions(rule_data['actions'])
                errors.extend(action_errors)
            
            # Check for discriminatory practices
            discrimination_warnings = self._check_discrimination(rule_data.get('conditions', {}))
            warnings.extend(discrimination_warnings)
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _get_applicable_rules(self, company_id: Optional[int] = None) -> List[DemographicRule]:
        """Get applicable demographic rules, with caching."""
        current_time = datetime.now()
        
        # Check cache validity
        if (self._cache_timestamp and 
            (current_time - self._cache_timestamp).seconds < self._cache_ttl):
            return self._rule_cache.get('rules', [])
        
        # Query database for active rules
        query = self.db.query(DemographicRule).filter(
            DemographicRule.is_active == True
        ).order_by(DemographicRule.priority.asc())
        
        rules = query.all()
        
        # Update cache
        self._rule_cache = {'rules': rules}
        self._cache_timestamp = current_time
        
        return rules
    
    def _profile_to_context(self, profile: CustomerProfile) -> Dict[str, Any]:
        """Convert customer profile to evaluation context."""
        context = {}
        
        # Basic demographic fields
        for field in self.ALLOWED_FIELDS:
            value = getattr(profile, field, None)
            if value is not None:
                context[field] = value
        
        # Convert boolean fields
        if hasattr(profile, 'islamic_finance_preference'):
            context['islamic_finance_preference'] = bool(profile.islamic_finance_preference)
        
        # Parse JSON fields
        if hasattr(profile, 'financial_goals') and profile.financial_goals:
            try:
                context['financial_goals'] = json.loads(profile.financial_goals) if isinstance(profile.financial_goals, str) else profile.financial_goals
            except (json.JSONDecodeError, TypeError):
                pass
        
        return context
    
    def _evaluate_single_rule(
        self, 
        rule: DemographicRule, 
        context: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """Evaluate a single demographic rule against context."""
        try:
            # Parse conditions if they're stored as string
            conditions = rule.conditions
            if isinstance(conditions, str):
                conditions = json.loads(conditions)
            
            # Evaluate conditions
            matched = self._evaluate_conditions(conditions, context)
            
            # Parse actions if they're stored as string
            actions = rule.actions
            if isinstance(actions, str):
                actions = json.loads(actions)
            
            return RuleEvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                matched=matched,
                actions=actions if matched else {},
                priority=rule.priority,
                evaluation_details={
                    'conditions': conditions,
                    'context_keys': list(context.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
            return RuleEvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                matched=False,
                actions={},
                priority=rule.priority,
                evaluation_details={'error': str(e)}
            )
    
    def _evaluate_conditions(
        self, 
        conditions: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> bool:
        """Recursively evaluate rule conditions."""
        if not isinstance(conditions, dict):
            return False
        
        # Handle logical operators
        if LogicalOperator.AND in conditions:
            and_conditions = conditions[LogicalOperator.AND]
            if not isinstance(and_conditions, list):
                return False
            return all(self._evaluate_conditions(cond, context) for cond in and_conditions)
        
        if LogicalOperator.OR in conditions:
            or_conditions = conditions[LogicalOperator.OR]
            if not isinstance(or_conditions, list):
                return False
            return any(self._evaluate_conditions(cond, context) for cond in or_conditions)
        
        if LogicalOperator.NOT in conditions:
            not_condition = conditions[LogicalOperator.NOT]
            return not self._evaluate_conditions(not_condition, context)
        
        # Handle field conditions
        for field, condition in conditions.items():
            if field in {LogicalOperator.AND, LogicalOperator.OR, LogicalOperator.NOT}:
                continue
                
            if not self._evaluate_field_condition(field, condition, context):
                return False
        
        return True
    
    def _evaluate_field_condition(
        self, 
        field: str, 
        condition: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single field condition."""
        if field not in context:
            return False
        
        field_value = context[field]
        
        for operator, expected_value in condition.items():
            if not self._apply_operator(field_value, operator, expected_value):
                return False
        
        return True
    
    def _apply_operator(self, field_value: Any, operator: str, expected_value: Any) -> bool:
        """Apply a comparison operator."""
        try:
            if operator == RuleOperator.EQ:
                return field_value == expected_value
            elif operator == RuleOperator.NE:
                return field_value != expected_value
            elif operator == RuleOperator.GT:
                return field_value > expected_value
            elif operator == RuleOperator.GTE:
                return field_value >= expected_value
            elif operator == RuleOperator.LT:
                return field_value < expected_value
            elif operator == RuleOperator.LTE:
                return field_value <= expected_value
            elif operator == RuleOperator.IN:
                return field_value in expected_value if isinstance(expected_value, (list, tuple, set)) else False
            elif operator == RuleOperator.NOT_IN:
                return field_value not in expected_value if isinstance(expected_value, (list, tuple, set)) else True
            elif operator == RuleOperator.CONTAINS:
                return str(expected_value) in str(field_value)
            elif operator == RuleOperator.STARTS_WITH:
                return str(field_value).startswith(str(expected_value))
            elif operator == RuleOperator.ENDS_WITH:
                return str(field_value).endswith(str(expected_value))
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except Exception as e:
            logger.error(f"Error applying operator {operator}: {str(e)}")
            return False
    
    def _validate_conditions(self, conditions: Dict[str, Any]) -> List[str]:
        """Validate rule conditions structure."""
        errors = []
        
        if not isinstance(conditions, dict):
            errors.append("Conditions must be a dictionary")
            return errors
        
        # Validate logical operators
        logical_ops = {LogicalOperator.AND, LogicalOperator.OR, LogicalOperator.NOT}
        has_logical_op = any(op in conditions for op in logical_ops)
        
        if has_logical_op:
            # Validate logical operator structure
            for op in logical_ops:
                if op in conditions:
                    if op == LogicalOperator.NOT:
                        if not isinstance(conditions[op], dict):
                            errors.append(f"'{op}' operator must contain a dictionary")
                    else:
                        if not isinstance(conditions[op], list):
                            errors.append(f"'{op}' operator must contain a list")
                        else:
                            for i, sub_condition in enumerate(conditions[op]):
                                if not isinstance(sub_condition, dict):
                                    errors.append(f"'{op}' condition {i} must be a dictionary")
        else:
            # Validate field conditions
            for field, condition in conditions.items():
                if field not in self.ALLOWED_FIELDS:
                    errors.append(f"Field '{field}' is not allowed in rules")
                
                if not isinstance(condition, dict):
                    errors.append(f"Condition for field '{field}' must be a dictionary")
                    continue
                
                # Validate operators
                for operator in condition.keys():
                    if operator not in [op.value for op in RuleOperator]:
                        errors.append(f"Unknown operator '{operator}' for field '{field}'")
        
        return errors
    
    def _validate_actions(self, actions: Dict[str, Any]) -> List[str]:
        """Validate rule actions structure."""
        errors = []
        
        if not isinstance(actions, dict):
            errors.append("Actions must be a dictionary")
            return errors
        
        valid_actions = {'include_questions', 'exclude_questions', 'add_questions'}
        
        for action, value in actions.items():
            if action not in valid_actions:
                errors.append(f"Unknown action '{action}'")
                continue
            
            if not isinstance(value, list):
                errors.append(f"Action '{action}' must contain a list of question IDs")
                continue
            
            # Validate question IDs exist
            for question_id in value:
                if not isinstance(question_id, str):
                    errors.append(f"Question ID in '{action}' must be a string")
                elif not question_lookup.get_question_by_id(question_id):
                    errors.append(f"Question ID '{question_id}' in '{action}' does not exist")
        
        return errors
    
    def _check_discrimination(self, conditions: Dict[str, Any]) -> List[str]:
        """Check for potentially discriminatory rule conditions."""
        warnings = []
        
        def check_conditions_recursive(cond_dict):
            if not isinstance(cond_dict, dict):
                return
            
            for key, value in cond_dict.items():
                if key in self.PROTECTED_FIELDS:
                    warnings.append(
                        f"Rule uses protected field '{key}' which may be discriminatory. "
                        f"Please ensure this is legally compliant and necessary."
                    )
                elif isinstance(value, dict):
                    check_conditions_recursive(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            check_conditions_recursive(item)
        
        check_conditions_recursive(conditions)
        return warnings
    
    def _generate_profile_hash(self, profile: CustomerProfile) -> str:
        """Generate a hash for the demographic profile for caching."""
        import hashlib
        
        # Create a consistent string representation of relevant profile fields
        profile_data = {}
        for field in self.ALLOWED_FIELDS:
            value = getattr(profile, field, None)
            if value is not None:
                profile_data[field] = str(value)
        
        # Sort keys for consistent hashing
        profile_str = json.dumps(profile_data, sort_keys=True)
        return hashlib.md5(profile_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the rule cache."""
        self._rule_cache = {}
        self._cache_timestamp = None