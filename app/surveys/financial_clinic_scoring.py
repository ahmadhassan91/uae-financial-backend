"""
Financial Clinic Scoring Engine
Calculates 0-100 scores with 6-category breakdown

This module implements the Financial Clinic scoring methodology with:
- 0-100 score range (not 15-75)
- Weighted calculation based on question importance
- 6-category breakdown (15 questions total)
- 4 status bands: Excellent, Good, Needs Improvement, At Risk
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
    
    # Score band thresholds (aligned with design document)
    # 80%-100%: Excellent
    # >= 60% - 79%: Good
    # <= 30% < 59%: Needs Improvement (30-59)
    # <= 29%: At Risk
    SCORE_BANDS = {
        "Excellent": (80, 100),
        "Good": (60, 79),
        "Needs Improvement": (30, 59),
        "At Risk": (0, 29),
    }
    
    # Category status levels (percentage-based)
    CATEGORY_STATUS_THRESHOLDS = {
        "excellent": 80,   # 80-100% = excellent
        "good": 40,        # 40-79% = good  
        "at_risk": 0,      # 0-39% = at_risk
    }
    
    def __init__(self):
        """Initialize scorer with question definitions."""
        self.questions = FINANCIAL_CLINIC_QUESTIONS
        
    def calculate_score(
        self,
        responses: Dict[str, int],
        children_count: int = 0
    ) -> FinancialClinicScore:
        """
        Calculate complete Financial Clinic score.
        
        Args:
            responses: Dict of question_id -> answer_value (1-5)
                      Can contain 14 or 15 responses depending on children_count
            children_count: Number of children (0 = no children, >= 1 = has children)
            
        Returns:
            FinancialClinicScore with all calculations
            
        Example:
            responses = {
                "fc_q1": 4,  # "Well" = 4 points
                "fc_q2": 5,  # "Yes, multiple sources" = 5 points
                ...
                "fc_q15": 3,  # Only if has children
            }
        """
        # Get applicable questions based on children status
        applicable_questions = get_questions_for_profile(children_count=children_count)
        
        # If no children, add default score of 5 for Q15
        working_responses = responses.copy()
        if children_count == 0 and "fc_q15" not in working_responses:
            # Default score of 5 for Q15 when user has no children
            working_responses["fc_q15"] = 5
        
        # Calculate category scores
        category_scores = {}
        total_score = 0.0
        
        for category in FinancialClinicCategory:
            category_score = self._calculate_category_score(
                category,
                working_responses,
                children_count
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
            total_questions=15  # Always 15 questions (Q15 auto-scored if no children)
        )
    
    def _calculate_category_score(
        self,
        category: FinancialClinicCategory,
        responses: Dict[str, int],
        children_count: int = 0
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
        # Get ALL questions for this category (including conditional ones)
        # We need to calculate using all questions to maintain proper weighting
        category_questions = [
            q for q in FINANCIAL_CLINIC_QUESTIONS
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
        children_count: int = 0
    ) -> Tuple[bool, List[str]]:
        """
        Validate survey responses.
        
        Args:
            responses: Survey responses to validate
            children_count: Number of children (0 = no children, >= 1 = has children)
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        applicable_questions = get_questions_for_profile(children_count=children_count)
        
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
    children_count: int = 0
) -> Dict:
    """
    Convenience function to calculate score and return as dict.
    
    Args:
        responses: Question responses (question_id -> answer_value)
                  Can contain 14 or 15 responses depending on children_count
        children_count: Number of children (0 = no children, >= 1 = has children)
        
    Returns:
        Dictionary with score breakdown
    """
    scorer = FinancialClinicScorer()
    score_result = scorer.calculate_score(responses, children_count=children_count)
    
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
