"""
Financial Clinic Scoring Engine
Calculates 0-100 scores with 6-category breakdown

This module implements the Financial Clinic scoring methodology with:
- 0-100 score range (not 15-75)
- Weighted calculation based on question importance
- 6-category breakdown
- Conditional Q16 handling
- Status band determination
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .financial_clinic_questions import (
    FINANCIAL_CLINIC_QUESTIONS,
    FinancialClinicCategory,
    CATEGORY_WEIGHTS,
    get_questions_for_profile
)


@dataclass
class CategoryScore:
    """Score for a single category."""
    category: FinancialClinicCategory
    score: float  # 0-100 percentage
    max_possible: float
    actual_points: float
    status_level: str  # "at_risk", "good", "excellent"


@dataclass
class FinancialClinicScore:
    """Complete Financial Clinic scoring result."""
    total_score: float  # 0-100
    category_scores: Dict[str, CategoryScore]
    status_band: str  # Overall status
    questions_answered: int
    total_questions: int
    

class FinancialClinicScorer:
    """Calculate Financial Clinic scores using weighted methodology."""
    
    # Score band thresholds
    SCORE_BANDS = {
        "Excellent": (81, 100),
        "Good": (61, 80),
        "Moderate": (41, 60),
        "Needs Immediate Attention": (21, 40),
        "At Risk": (0, 20),
    }
    
    # Category status levels (used for insights and products)
    CATEGORY_STATUS_THRESHOLDS = {
        "excellent": 81,  # 81-100%
        "good": 41,       # 41-80%
        "at_risk": 0,     # 0-40%
    }
    
    def __init__(self):
        """Initialize scorer with question definitions."""
        self.questions = FINANCIAL_CLINIC_QUESTIONS
        
    def calculate_score(
        self,
        responses: Dict[str, int],
        has_children: bool = False
    ) -> FinancialClinicScore:
        """
        Calculate complete Financial Clinic score.
        
        Args:
            responses: Dict of question_id -> answer_value (1-5)
            has_children: Whether customer has children (affects Q16)
            
        Returns:
            FinancialClinicScore with all calculations
            
        Example:
            responses = {
                "fc_q1": 4,  # "Well" = 4 points
                "fc_q2": 5,  # "Yes, multiple sources" = 5 points
                ...
            }
        """
        # Get applicable questions
        applicable_questions = get_questions_for_profile(has_children)
        
        # Calculate category scores
        category_scores = {}
        total_score = 0.0
        
        for category in FinancialClinicCategory:
            category_score = self._calculate_category_score(
                category,
                responses,
                applicable_questions
            )
            category_scores[category.value] = category_score
            total_score += category_score.score
        
        # Determine overall status band
        status_band = self._get_status_band(total_score)
        
        return FinancialClinicScore(
            total_score=round(total_score, 2),
            category_scores=category_scores,
            status_band=status_band,
            questions_answered=len(responses),
            total_questions=len(applicable_questions)
        )
    
    def _calculate_category_score(
        self,
        category: FinancialClinicCategory,
        responses: Dict[str, int],
        applicable_questions: List
    ) -> CategoryScore:
        """
        Calculate score for a single category.
        
        Formula:
        Category Score = Σ(Answer Value × Question Weight) for all questions in category
        
        Example for Income Stream:
        - Q1 (5% weight): Answer=4 → 4 × 5 = 20 points
        - Q2 (10% weight): Answer=5 → 5 × 10 = 50 points
        - Total: 20 + 50 = 70 points out of 75 possible (93.3%)
        - But category is only 15% of total, so: 93.3% × 15% = 14.0 points
        """
        # Get questions for this category
        category_questions = [
            q for q in applicable_questions
            if q.category == category
        ]
        
        if not category_questions:
            return CategoryScore(
                category=category,
                score=0.0,
                max_possible=0.0,
                actual_points=0.0,
                status_level="at_risk"
            )
        
        # Calculate weighted score
        actual_points = 0.0
        max_possible = 0.0
        
        for question in category_questions:
            answer_value = responses.get(question.id, 0)
            question_weight = question.weight
            
            # Points earned = answer_value × weight
            actual_points += answer_value * question_weight
            
            # Max possible = 5 (best answer) × weight
            max_possible += 5 * question_weight
        
        # Calculate percentage score for this category
        if max_possible > 0:
            category_percentage = (actual_points / max_possible) * 100
        else:
            category_percentage = 0.0
        
        # The category contributes its percentage of total score
        # For example, if Income Stream (15%) scores 80%, it contributes 12 points to total
        category_weight = CATEGORY_WEIGHTS.get(category, 0)
        contribution_to_total = (category_percentage / 100) * category_weight
        
        # Determine status level
        status_level = self._get_category_status(category_percentage)
        
        return CategoryScore(
            category=category,
            score=round(contribution_to_total, 2),
            max_possible=category_weight,
            actual_points=round(actual_points, 2),
            status_level=status_level
        )
    
    def _get_status_band(self, total_score: float) -> str:
        """Determine overall status band from total score."""
        for band_name, (min_score, max_score) in self.SCORE_BANDS.items():
            if min_score <= total_score <= max_score:
                return band_name
        return "At Risk"  # Default
    
    def _get_category_status(self, category_percentage: float) -> str:
        """
        Determine category status level for insights/products.
        
        Args:
            category_percentage: Category score as percentage (0-100)
            
        Returns:
            "excellent", "good", or "at_risk"
        """
        if category_percentage >= self.CATEGORY_STATUS_THRESHOLDS["excellent"]:
            return "excellent"
        elif category_percentage >= self.CATEGORY_STATUS_THRESHOLDS["good"]:
            return "good"
        else:
            return "at_risk"
    
    def validate_responses(
        self,
        responses: Dict[str, int],
        has_children: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate survey responses.
        
        Args:
            responses: Survey responses to validate
            has_children: Whether customer has children
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        applicable_questions = get_questions_for_profile(has_children)
        
        # Check all required questions answered
        for question in applicable_questions:
            if question.id not in responses:
                errors.append(f"Missing answer for question {question.number}")
        
        # Validate answer values
        for question_id, answer_value in responses.items():
            if not (1 <= answer_value <= 5):
                errors.append(
                    f"Invalid answer value {answer_value} for {question_id}. "
                    f"Must be 1-5."
                )
        
        return (len(errors) == 0, errors)


def calculate_financial_clinic_score(
    responses: Dict[str, int],
    has_children: bool = False
) -> Dict:
    """
    Convenience function to calculate score and return as dict.
    
    Args:
        responses: Question responses (question_id -> answer_value)
        has_children: Whether customer has children
        
    Returns:
        Dictionary with score breakdown
    """
    scorer = FinancialClinicScorer()
    score_result = scorer.calculate_score(responses, has_children)
    
    return {
        "total_score": score_result.total_score,
        "status_band": score_result.status_band,
        "category_scores": {
            category_name: {
                "score": cat_score.score,
                "max_possible": cat_score.max_possible,
                "percentage": round((cat_score.score / cat_score.max_possible * 100), 2) if cat_score.max_possible > 0 else 0,
                "status_level": cat_score.status_level
            }
            for category_name, cat_score in score_result.category_scores.items()
        },
        "questions_answered": score_result.questions_answered,
        "total_questions": score_result.total_questions
    }
