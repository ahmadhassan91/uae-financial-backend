"""Company question set management service."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import json
import hashlib

from ..models import (
    CompanyTracker, QuestionVariation, DemographicRule, 
    CustomerProfile, CompanyQuestionSet
)
from ..surveys.dynamic_question_engine import DynamicQuestionEngine
from ..surveys.question_definitions import SURVEY_QUESTIONS_V2
from ..database import get_db


class CompanyQuestionManager:
    """Manages custom question sets for companies."""
    
    def __init__(self, db: Session):
        self.db = db
        self.dynamic_engine = DynamicQuestionEngine(db)
    
    async def get_company_question_set(
        self,
        company_url: str,
        demographic_profile: Optional[CustomerProfile] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get the question set for a specific company URL."""
        
        # Find company by URL
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url,
            CompanyTracker.is_active == True
        ).first()
        
        if not company:
            # Return default question set if company not found
            return await self._get_default_question_set(demographic_profile, language)
        
        # Get company's custom question set
        question_set = self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.company_tracker_id == company.id,
            CompanyQuestionSet.is_active == True
        ).first()
        
        if not question_set:
            # Return default with company branding if no custom set
            default_set = await self._get_default_question_set(demographic_profile, language)
            default_set["company_config"] = {
                "company_id": company.id,
                "company_name": company.company_name,
                "branding": company.custom_branding or {},
                "question_set_id": "default"
            }
            return default_set
        
        # Build custom question set
        return await self._build_custom_question_set(
            question_set, company, demographic_profile, language
        )
    
    async def create_custom_question_set(
        self,
        company_id: int,
        name: str,
        base_questions: List[str],
        custom_questions: Optional[List[Dict]] = None,
        excluded_questions: Optional[List[str]] = None,
        question_variations: Optional[Dict[str, str]] = None,
        demographic_rules: Optional[List[Dict]] = None,
        description: Optional[str] = None
    ) -> CompanyQuestionSet:
        """Create a new custom question set for a company."""
        
        # Validate company exists
        company = self.db.query(CompanyTracker).filter(
            CompanyTracker.id == company_id
        ).first()
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        # Validate base questions exist
        valid_question_ids = {q.id for q in SURVEY_QUESTIONS_V2}
        
        invalid_questions = set(base_questions) - valid_question_ids
        if invalid_questions:
            raise ValueError(f"Invalid question IDs: {invalid_questions}")
        
        # Validate excluded questions
        if excluded_questions:
            invalid_excluded = set(excluded_questions) - valid_question_ids
            if invalid_excluded:
                raise ValueError(f"Invalid excluded question IDs: {invalid_excluded}")
        
        # Validate question variations
        if question_variations:
            for base_id, variation_id in question_variations.items():
                if base_id not in valid_question_ids:
                    raise ValueError(f"Invalid base question ID: {base_id}")
                
                # Check if variation exists
                variation = self.db.query(QuestionVariation).filter(
                    QuestionVariation.base_question_id == base_id,
                    QuestionVariation.variation_name == variation_id,
                    QuestionVariation.is_active == True
                ).first()
                if not variation:
                    raise ValueError(f"Variation '{variation_id}' not found for question '{base_id}'")
        
        # Deactivate existing question sets for this company
        self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.company_tracker_id == company_id,
            CompanyQuestionSet.is_active == True
        ).update({"is_active": False})
        
        # Create new question set
        question_set = CompanyQuestionSet(
            company_tracker_id=company_id,
            name=name,
            description=description,
            base_questions=base_questions,
            custom_questions=custom_questions or [],
            excluded_questions=excluded_questions or [],
            question_variations=question_variations or {},
            demographic_rules=demographic_rules or []
        )
        
        self.db.add(question_set)
        self.db.commit()
        self.db.refresh(question_set)
        
        return question_set
    
    async def update_question_set(
        self,
        question_set_id: int,
        **updates
    ) -> CompanyQuestionSet:
        """Update an existing question set."""
        
        question_set = self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.id == question_set_id
        ).first()
        
        if not question_set:
            raise ValueError(f"Question set with ID {question_set_id} not found")
        
        # Create new version instead of updating existing
        new_version = CompanyQuestionSet(
            company_tracker_id=question_set.company_tracker_id,
            name=updates.get("name", question_set.name),
            description=updates.get("description", question_set.description),
            base_questions=updates.get("base_questions", question_set.base_questions),
            custom_questions=updates.get("custom_questions", question_set.custom_questions),
            excluded_questions=updates.get("excluded_questions", question_set.excluded_questions),
            question_variations=updates.get("question_variations", question_set.question_variations),
            demographic_rules=updates.get("demographic_rules", question_set.demographic_rules)
        )
        
        # Deactivate old version
        question_set.is_active = False
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version
    
    async def get_question_set_versions(
        self,
        company_id: int
    ) -> List[CompanyQuestionSet]:
        """Get all versions of question sets for a company."""
        
        return self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.company_tracker_id == company_id
        ).order_by(CompanyQuestionSet.created_at.desc()).all()
    
    async def rollback_to_version(
        self,
        company_id: int,
        version_id: int
    ) -> CompanyQuestionSet:
        """Rollback to a previous version of the question set."""
        
        # Find the version to rollback to
        target_version = self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.id == version_id,
            CompanyQuestionSet.company_tracker_id == company_id
        ).first()
        
        if not target_version:
            raise ValueError(f"Version {version_id} not found for company {company_id}")
        
        # Deactivate current active version
        self.db.query(CompanyQuestionSet).filter(
            CompanyQuestionSet.company_tracker_id == company_id,
            CompanyQuestionSet.is_active == True
        ).update({"is_active": False})
        
        # Create new active version based on target
        new_version = CompanyQuestionSet(
            company_tracker_id=target_version.company_tracker_id,
            name=f"{target_version.name} (Restored)",
            description=f"Restored from version created at {target_version.created_at}",
            base_questions=target_version.base_questions,
            custom_questions=target_version.custom_questions,
            excluded_questions=target_version.excluded_questions,
            question_variations=target_version.question_variations,
            demographic_rules=target_version.demographic_rules
        )
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version
    
    async def get_question_set_analytics(
        self,
        company_id: int,
        question_set_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get analytics for company question sets."""
        
        from ..models import SurveyResponse
        
        # Base query for company responses
        query = self.db.query(SurveyResponse).filter(
            SurveyResponse.company_tracker_id == company_id
        )
        
        if question_set_id:
            query = query.filter(
                SurveyResponse.question_set_id == str(question_set_id)
            )
        
        responses = query.all()
        
        if not responses:
            return {
                "total_responses": 0,
                "completion_rate": 0,
                "average_score": 0,
                "question_performance": {},
                "demographic_breakdown": {}
            }
        
        # Calculate metrics
        total_responses = len(responses)
        total_score = sum(r.overall_score for r in responses)
        average_score = total_score / total_responses
        
        # Question performance analysis
        question_performance = {}
        demographic_breakdown = {}
        
        for response in responses:
            # Analyze individual question responses
            if response.responses:
                for question_id, answer in response.responses.items():
                    if question_id not in question_performance:
                        question_performance[question_id] = {
                            "total_responses": 0,
                            "average_score": 0,
                            "score_distribution": {}
                        }
                    
                    question_performance[question_id]["total_responses"] += 1
                    
                    # Track score distribution
                    score_key = str(answer)
                    if score_key not in question_performance[question_id]["score_distribution"]:
                        question_performance[question_id]["score_distribution"][score_key] = 0
                    question_performance[question_id]["score_distribution"][score_key] += 1
            
            # Demographic breakdown
            if response.customer_profile:
                profile = response.customer_profile
                demo_key = f"{profile.nationality}_{profile.age_group if hasattr(profile, 'age_group') else 'unknown'}"
                
                if demo_key not in demographic_breakdown:
                    demographic_breakdown[demo_key] = {
                        "count": 0,
                        "average_score": 0,
                        "total_score": 0
                    }
                
                demographic_breakdown[demo_key]["count"] += 1
                demographic_breakdown[demo_key]["total_score"] += response.overall_score
                demographic_breakdown[demo_key]["average_score"] = (
                    demographic_breakdown[demo_key]["total_score"] / 
                    demographic_breakdown[demo_key]["count"]
                )
        
        return {
            "total_responses": total_responses,
            "average_score": round(average_score, 2),
            "question_performance": question_performance,
            "demographic_breakdown": demographic_breakdown,
            "score_distribution": {
                "excellent": len([r for r in responses if r.overall_score >= 80]),
                "good": len([r for r in responses if 60 <= r.overall_score < 80]),
                "fair": len([r for r in responses if 40 <= r.overall_score < 60]),
                "poor": len([r for r in responses if r.overall_score < 40])
            }
        }
    
    async def _get_default_question_set(
        self,
        demographic_profile: Optional[CustomerProfile] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get the default question set."""
        
        questions = await self.dynamic_engine.get_questions_for_profile(
            demographic_profile, language=language
        )
        
        return {
            "questions": questions,
            "question_set_id": "default",
            "company_config": None,
            "metadata": {
                "total_questions": len(questions),
                "language": language,
                "demographic_rules_applied": []
            }
        }
    
    async def _build_custom_question_set(
        self,
        question_set: CompanyQuestionSet,
        company: CompanyTracker,
        demographic_profile: Optional[CustomerProfile] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Build a custom question set based on company configuration."""
        
        questions_dict = {q.id: q for q in SURVEY_QUESTIONS_V2}
        
        # Start with base questions
        selected_questions = []
        for question_id in question_set.base_questions:
            if question_id in questions_dict and question_id not in (question_set.excluded_questions or []):
                question_def = questions_dict[question_id]
                question = {
                    "id": question_def.id,
                    "text": question_def.text,
                    "options": [{"value": opt.value, "label": opt.label} for opt in question_def.options],
                    "factor": question_def.factor.value,
                    "weight": question_def.weight,
                    "type": question_def.type,
                    "required": question_def.required
                }
                
                # Apply question variations if configured
                if question_set.question_variations and question_id in question_set.question_variations:
                    variation_name = question_set.question_variations[question_id]
                    variation = self.db.query(QuestionVariation).filter(
                        QuestionVariation.base_question_id == question_id,
                        QuestionVariation.variation_name == variation_name,
                        QuestionVariation.language == language,
                        QuestionVariation.is_active == True
                    ).first()
                    
                    if variation:
                        question.update({
                            "text": variation.text,
                            "options": variation.options,
                            "variation_used": variation_name
                        })
                
                selected_questions.append(question)
        
        # Add custom questions if any
        if question_set.custom_questions:
            selected_questions.extend(question_set.custom_questions)
        
        # Apply demographic rules if configured
        demographic_rules_applied = []
        if question_set.demographic_rules and demographic_profile:
            for rule_config in question_set.demographic_rules:
                if self._evaluate_demographic_rule(rule_config, demographic_profile):
                    demographic_rules_applied.append(rule_config.get("name", "unnamed_rule"))
                    
                    # Apply rule actions
                    actions = rule_config.get("actions", {})
                    
                    # Include additional questions
                    if "include_questions" in actions:
                        for question_id in actions["include_questions"]:
                            if question_id in questions_dict:
                                question_def = questions_dict[question_id]
                                question = {
                                    "id": question_def.id,
                                    "text": question_def.text,
                                    "options": [{"value": opt.value, "label": opt.label} for opt in question_def.options],
                                    "factor": question_def.factor.value,
                                    "weight": question_def.weight,
                                    "type": question_def.type,
                                    "required": question_def.required
                                }
                                if question not in selected_questions:
                                    selected_questions.append(question)
                    
                    # Exclude questions
                    if "exclude_questions" in actions:
                        selected_questions = [
                            q for q in selected_questions 
                            if q["id"] not in actions["exclude_questions"]
                        ]
        
        return {
            "questions": selected_questions,
            "question_set_id": str(question_set.id),
            "company_config": {
                "company_id": company.id,
                "company_name": company.company_name,
                "branding": company.custom_branding or {},
                "question_set_name": question_set.name
            },
            "metadata": {
                "total_questions": len(selected_questions),
                "language": language,
                "demographic_rules_applied": demographic_rules_applied,
                "base_questions_count": len(question_set.base_questions),
                "custom_questions_count": len(question_set.custom_questions or []),
                "excluded_questions_count": len(question_set.excluded_questions or [])
            }
        }
    
    def _evaluate_demographic_rule(
        self,
        rule_config: Dict[str, Any],
        profile: CustomerProfile
    ) -> bool:
        """Evaluate if a demographic rule matches the profile."""
        
        conditions = rule_config.get("conditions", {})
        
        def evaluate_condition(condition: Dict[str, Any]) -> bool:
            if "and" in condition:
                return all(evaluate_condition(c) for c in condition["and"])
            elif "or" in condition:
                return any(evaluate_condition(c) for c in condition["or"])
            else:
                # Single condition
                for field, criteria in condition.items():
                    profile_value = getattr(profile, field, None)
                    
                    if "eq" in criteria:
                        return profile_value == criteria["eq"]
                    elif "in" in criteria:
                        return profile_value in criteria["in"]
                    elif "gte" in criteria:
                        return profile_value >= criteria["gte"]
                    elif "lte" in criteria:
                        return profile_value <= criteria["lte"]
                    elif "gt" in criteria:
                        return profile_value > criteria["gt"]
                    elif "lt" in criteria:
                        return profile_value < criteria["lt"]
                
                return False
        
        return evaluate_condition(conditions)


