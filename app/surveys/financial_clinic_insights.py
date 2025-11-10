"""
Financial Clinic Insights Matrix
18 Personalized Insights (6 categories × 3 status levels)

This module provides personalized financial insights based on:
- Category scores (Income Stream, Savings Habit, etc.)
- Status levels (At Risk, Good, Excellent)
- Category priority hierarchy for ranking
- Profile data (income, nationality, gender, children) for conditional insights

Maximum 5 insights displayed, ranked from lowest to highest score with priority hierarchy.
"""
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from .financial_clinic_questions import FinancialClinicCategory


@dataclass
class Insight:
    """A personalized financial insight."""
    category: str
    status_level: str
    text: str
    priority: int  # Lower number = higher priority


# 18 Insights Matrix (6 categories × 3 status levels)
# Conditional logic based on design specifications:
# - Income > 30K: income ranges "30,000 to 40,000", "40,000 to 50,000", "50,000 to 100,000", "Above 100,000"
# - Income < 30K: income ranges "Below 5,000", "5,000 to 10,000", "10,000 to 20,000", "20,000 to 30,000"
# - Children = 0: no children
# - Children > 0: has children (1, 2, 3, 4, 5+)
# - Emirati & Woman: nationality = "Emirati" AND gender = "Female"
# - "Else": general fallback
INSIGHTS_MATRIX: Dict[str, Dict[str, Dict[str, str]]] = {
    FinancialClinicCategory.INCOME_STREAM.value: {
        "at_risk": {
            "default": (
                "Your income sources seem limited or inconsistent. Focus on creating stability by building "
                "a consistent income stream and a small safety buffer with our regular saving plans starting "
                "with AED 100"
            ),
        },
        "good": {
            "default": (
                "Your income is steady but could be diversified. Explore additional or passive income sources "
                "such as our Second Salary Plan, to strengthen financial resilience."
            ),
        },
        "excellent": {
            "income_above_30k": (
                "You have a stable, consistent income. Now focus on long-term growth and wealth accumulation "
                "through My Million plan"
            ),
            "default": (
                "You have a stable, consistent income. Now focus on long-term growth and wealth-building opportunities."
            ),
        },
    },
    FinancialClinicCategory.SAVINGS_HABIT.value: {
        "at_risk": {
            "income_below_30k": (
                "Your savings habits are irregular or minimal. Start small with automated monthly contributions to build "
                "consistency and discipline through myPlan."
            ),
            "income_above_30k": (
                "Your savings habit seems irregular or minimal. Increase your savings safety net with Saving Bonds"
            ),
            "default": (
                "Your saving habits are irregular or minimal. Start small with automated monthly contributions to build "
                "consistency and discipline through myPlan."
            ),
        },
        "good": {
            "default": (
                "You save occasionally, but your rate could improve. Set clear goals and increase your savings "
                "percentage gradually"
            ),
        },
        "excellent": {
            "default": (
                "You maintain a strong savings routine. Continue optimizing returns through structured plans and "
                "smart investments. Consider long term savings with our Booster offerings for enhanced savings "
                "growth over 3 to 5 years"
            ),
        },
    },
    FinancialClinicCategory.EMERGENCY_SAVINGS.value: {
        "at_risk": {
            "default": (
                "You may not have enough set aside for unexpected expenses. Aim for at least 3 months of essential living costs with myPlan."
            ),
        },
        "good": {
            "emirati_woman": (
                "You've built a partial safety net. Keep growing it to cover 6 months of living expenses for stronger security. "
                "Enhance your emergency savings with Ahed savings plan"
            ),
            "else": (
                "Enhance your emergency savings with our myPlan monthly savings plan"
            ),
            "default": (
                "You've built a partial safety net. Keep growing it to cover 6 months of living expenses for stronger security."
            ),
        },
        "excellent": {
            "default": (
                "You're well-prepared for emergencies. Consider investing your surplus for sustainable long-term growth with National Bonds Term "
                "Sukuk or Booster Offerings"
            ),
        },
    },
    FinancialClinicCategory.DEBT_MANAGEMENT.value: {
        "at_risk": {
            "default": (
                "High debt levels or repayment habits may be limiting your flexibility. Prioritize reducing debt and avoid taking on new ones."
            ),
        },
        "good": {
            "default": (
                "You're managing debt reasonably well, but there's room to improve. Focus on timely payments and debt reduction strategies."
            ),
        },
        "excellent": {
            "default": (
                "You maintain excellent control over your debt. Use credit strategically to strengthen your financial profile."
            ),
        },
    },
    FinancialClinicCategory.RETIREMENT_PLANNING.value: {
        "at_risk": {
            "default": (
                "You haven't started preparing for retirement yet. Begin now, even small contributions can create big impact over time."
            ),
        },
        "good": {
            "income_above_30k": (
                "You've started saving but may not be contributing enough. Regularly review and increase your contributions toward "
                "your retirement plans with our My Million plan."
            ),
            "else": (
                "You've started saving but may not be contributing enough. Regularly review and increase your contributions toward "
                "your retirement goals with our Global Savings Club or Second Salary plan"
            ),
            "default": (
                "You've started saving but may not be contributing enough. Regularly review and increase your contributions toward "
                "your retirement plans."
            ),
        },
        "excellent": {
            "default": (
                "You're actively preparing for retirement. Keep your portfolio balanced for both income and lifestyle needs."
            ),
        },
    },
    FinancialClinicCategory.PROTECTING_FAMILY.value: {
        "at_risk": {
            "default": (
                "Your family may not have full financial protection. Explore saving and protection plans that safeguard your loved ones."
            ),
        },
        "good": {
            "children_zero": (
                "You have basic financial protection in place for your family, but coverage may be limited."
            ),
            "children_above_zero": (
                "You have some coverage, but it might be limited. Review your plans to ensure they align with your family's evolving needs. "
                "At the same time, you can start saving to secure your child's education with My Education Plan."
            ),
            "default": (
                "You have basic financial protection in place for your family, but coverage may be limited."
            ),
        },
        "excellent": {
            "children_zero": (
                "You have strong financial protection in place. Keep it updated as your lifestyle and responsibilities change. "
                "You can also strengthen to your family's financial future with My Million plan"
            ),
            "else": (
                "You can also save to secure your family's financial future with Junior Million plan"
            ),
            "default": (
                "You have strong financial protection in place. Keep it updated as your lifestyle and responsibilities change."
            ),
        },
    },
}


# Category priority for tie-breaking (1 = highest priority)
CATEGORY_PRIORITY: Dict[str, int] = {
    FinancialClinicCategory.INCOME_STREAM.value: 1,
    FinancialClinicCategory.EMERGENCY_SAVINGS.value: 2,
    FinancialClinicCategory.SAVINGS_HABIT.value: 3,
    FinancialClinicCategory.RETIREMENT_PLANNING.value: 4,
    FinancialClinicCategory.DEBT_MANAGEMENT.value: 5,
    FinancialClinicCategory.PROTECTING_FAMILY.value: 6,
}


class InsightsEngine:
    """Generate personalized insights based on category scores and profile data."""
    
    def __init__(self):
        """Initialize insights engine."""
        self.insights_matrix = INSIGHTS_MATRIX
        self.category_priority = CATEGORY_PRIORITY
    
    def get_insights(
        self,
        category_scores: Dict[str, Dict],
        profile: Optional[Dict[str, Any]] = None,
        max_insights: int = 5
    ) -> List[Insight]:
        """
        Get personalized insights based on category scores and profile data.
        
        Args:
            category_scores: Dict of category -> {score, status_level}
                Example:
                {
                    "Income Stream": {"score": 12.0, "status_level": "good"},
                    "Savings Habit": {"score": 8.5, "status_level": "at_risk"},
                    ...
                }
            profile: Optional profile data for conditional insights
                {
                    "income_range": "30K-50K",
                    "nationality": "Emirati",
                    "gender": "Female",
                    "children": 2
                }
            max_insights: Maximum number of insights to return (strictly enforced, default: 5)
            
        Returns:
            List of Insight objects, prioritized by lowest scores (max 5)
        """
        # Rank categories by score (lowest first)
        ranked_categories = self._rank_categories(category_scores)
        
        # Generate insights for top categories (strictly limited to max_insights)
        insights = []
        for category_name, score_data in ranked_categories[:max_insights]:
            status_level = score_data["status_level"]
            
            # Get conditional insight text based on profile
            insight_text = self._select_insight_text(
                category_name,
                status_level,
                profile or {}
            )
            
            if insight_text:
                insights.append(Insight(
                    category=category_name,
                    status_level=status_level,
                    text=insight_text,
                    priority=self.category_priority.get(category_name, 99)
                ))
        
        return insights
    
    def _select_insight_text(
        self,
        category: str,
        status_level: str,
        profile: Dict[str, Any]
    ) -> str:
        """
        Select appropriate insight text based on profile conditions.
        
        Conditions evaluated in order:
        1. Income > 30K or < 30K
        2. Children = 0 or > 0
        3. Emirati & Woman
        4. Else (fallback)
        5. Default
        
        Args:
            category: Category name
            status_level: "at_risk", "good", or "excellent"
            profile: Profile data
            
        Returns:
            Conditional insight text
        """
        category_insights = self.insights_matrix.get(category, {})
        status_insights = category_insights.get(status_level, {})
        
        if not status_insights:
            return ""
        
        # Parse income range
        income_range = profile.get("income_range", "")
        income_above_30k = self._is_income_above_30k(income_range)
        income_below_30k = self._is_income_below_30k(income_range)
        
        # Check children
        children = profile.get("children", 0)
        children_zero = children == 0
        children_above_zero = children > 0
        
        # Check Emirati & Woman
        nationality = profile.get("nationality", "")
        gender = profile.get("gender", "")
        is_emirati_woman = (nationality == "Emirati" and gender == "Female")
        
        # Priority order for condition checking:
        # 1. Income-based conditions
        if income_above_30k and "income_above_30k" in status_insights:
            return status_insights["income_above_30k"]
        
        if income_below_30k and "income_below_30k" in status_insights:
            return status_insights["income_below_30k"]
        
        # 2. Emirati woman condition
        if is_emirati_woman and "emirati_woman" in status_insights:
            return status_insights["emirati_woman"]
        
        # 3. Children-based conditions
        if children_zero and "children_zero" in status_insights:
            return status_insights["children_zero"]
        
        if children_above_zero and "children_above_zero" in status_insights:
            return status_insights["children_above_zero"]
        
        # 4. Else condition (fallback before default)
        if "else" in status_insights:
            return status_insights["else"]
        
        # 5. Default fallback
        return status_insights.get("default", "")
    
    def _is_income_above_30k(self, income_range: str) -> bool:
        """
        Check if income is above 30K AED.
        
        Args:
            income_range: Income range string
            
        Returns:
            True if income > 30K
        """
        high_income_ranges = [
            "30,000 to 40,000",
            "40,000 to 50,000",
            "50,000 to 100,000",
            "Above 100,000"
        ]
        return income_range in high_income_ranges
    
    def _is_income_below_30k(self, income_range: str) -> bool:
        """
        Check if income is below or equal to 30K AED.
        
        Args:
            income_range: Income range string
            
        Returns:
            True if income <= 30K
        """
        low_income_ranges = [
            "Below 5,000",
            "5,000 to 10,000",
            "10,000 to 20,000",
            "20,000 to 30,000"
        ]
        return income_range in low_income_ranges
    
    def _rank_categories(
        self,
        category_scores: Dict[str, Dict]
    ) -> List[Tuple[str, Dict]]:
        """
        Rank categories from lowest to highest score.
        Ties are broken using CATEGORY_PRIORITY.
        
        Args:
            category_scores: Category scores dictionary
            
        Returns:
            List of (category_name, score_data) tuples, sorted by priority
        """
        # Convert to list of tuples
        category_list = list(category_scores.items())
        
        # Sort by:
        # 1. Score (ascending - lowest first)
        # 2. Priority (ascending - higher priority first for ties)
        sorted_categories = sorted(
            category_list,
            key=lambda x: (
                x[1].get("score", 0),  # Lower score = higher priority
                self.category_priority.get(x[0], 99)  # Higher priority number for ties
            )
        )
        
        return sorted_categories
    
    def get_insight_for_category(
        self,
        category: str,
        status_level: str,
        profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get specific insight for a category and status level with profile conditions.
        
        Args:
            category: Category name
            status_level: "at_risk", "good", or "excellent"
            profile: Optional profile data for conditional insights
            
        Returns:
            Insight text
        """
        return self._select_insight_text(category, status_level, profile or {})


def generate_insights(
    category_scores: Dict[str, Dict],
    profile: Optional[Dict[str, Any]] = None,
    max_insights: int = 5
) -> List[Dict]:
    """
    Convenience function to generate insights with profile data.
    
    Args:
        category_scores: Category scores from scoring engine
        profile: Optional profile data for conditional insights
        max_insights: Maximum insights to return (strictly enforced at 5)
        
    Returns:
        List of insight dictionaries
    """
    engine = InsightsEngine()
    insights = engine.get_insights(category_scores, profile, max_insights)
    
    return [
        {
            "category": insight.category,
            "status_level": insight.status_level,
            "text": insight.text,
            "priority": insight.priority
        }
        for insight in insights
    ]
