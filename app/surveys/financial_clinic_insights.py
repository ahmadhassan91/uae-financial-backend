"""
Financial Clinic Insights Matrix
18 Personalized Insights (6 categories × 3 status levels)

This module provides personalized financial insights based on:
- Category scores (Income Stream, Savings Habit, etc.)
- Status levels (At Risk, Good, Excellent)
- Category priority hierarchy for ranking
"""
from typing import Dict, List, Tuple
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
INSIGHTS_MATRIX: Dict[str, Dict[str, str]] = {
    FinancialClinicCategory.INCOME_STREAM.value: {
        "at_risk": (
            "Your income sources appear limited or inconsistent. Consider building "
            "a safety net by diversifying income streams or exploring side opportunities."
        ),
        "good": (
            "Your income health is reasonable and can be improved by looking for "
            "multiple streams of income to increase financial resilience."
        ),
        "excellent": (
            "Your income stream is healthy and consistent. Continue to focus on "
            "long-term wealth building and optimizing your earning potential."
        ),
    },
    FinancialClinicCategory.SAVINGS_HABIT.value: {
        "at_risk": (
            "Your savings habit seems irregular or minimal. Start small with automatic "
            "monthly savings transfers to build consistency and discipline."
        ),
        "good": (
            "You're saving occasionally, but your savings rate could be higher. Try "
            "setting specific savings goals aligned with your financial priorities."
        ),
        "excellent": (
            "You have a healthy and consistent savings routine. You can now focus on "
            "optimizing returns through diversified investments."
        ),
    },
    FinancialClinicCategory.EMERGENCY_SAVINGS.value: {
        "at_risk": (
            "You do not have enough funds set aside for unexpected expenses. Aim to "
            "build an emergency fund covering at least 3-6 months of essential expenses."
        ),
        "good": (
            "You have a partial safety net, but it may not be sufficient for larger "
            "financial shocks. Work on increasing your emergency fund to 6 months of expenses."
        ),
        "excellent": (
            "You're well-prepared for emergencies with strong liquidity. You can now "
            "focus on investing surplus funds for long-term growth."
        ),
    },
    FinancialClinicCategory.DEBT_MANAGEMENT.value: {
        "at_risk": (
            "Your debt levels or repayment habits may be affecting your financial flexibility. "
            "Prioritize paying off high-interest debt and avoid taking on new debt."
        ),
        "good": (
            "You manage your debt moderately well, but there's room for improvement. "
            "Consider consolidating high-interest debts or increasing monthly payments."
        ),
        "excellent": (
            "You maintain excellent control over your debt. Continue this discipline "
            "and use credit strategically for wealth-building purposes."
        ),
    },
    FinancialClinicCategory.RETIREMENT_PLANNING.value: {
        "at_risk": (
            "You haven't yet started planning for retirement. Starting today, even with "
            "small contributions, can make a significant difference over time."
        ),
        "good": (
            "You have some plans for retirement but may not be saving enough. Consider "
            "increasing your contributions to retirement accounts and reviewing your investment strategy."
        ),
        "excellent": (
            "You're actively preparing for retirement. Keep reviewing your portfolio to "
            "ensure it is well-diversified and aligned with your long-term goals."
        ),
    },
    FinancialClinicCategory.PROTECTING_FAMILY.value: {
        "at_risk": (
            "You may not have adequate protection for yourself or your family. Explore "
            "Takaful (Islamic insurance) and savings plans to safeguard your loved ones."
        ),
        "good": (
            "You have basic financial protection for your family, but coverage may be "
            "limited. Review your insurance needs annually as your circumstances change."
        ),
        "excellent": (
            "You have built-in systems for financial protection. Keep your coverage "
            "updated as your family situation and financial goals evolve."
        ),
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
    """Generate personalized insights based on category scores."""
    
    def __init__(self):
        """Initialize insights engine."""
        self.insights_matrix = INSIGHTS_MATRIX
        self.category_priority = CATEGORY_PRIORITY
    
    def get_insights(
        self,
        category_scores: Dict[str, Dict],
        max_insights: int = 5
    ) -> List[Insight]:
        """
        Get personalized insights based on category scores.
        
        Args:
            category_scores: Dict of category -> {score, status_level}
                Example:
                {
                    "Income Stream": {"score": 12.0, "status_level": "good"},
                    "Savings Habit": {"score": 8.5, "status_level": "at_risk"},
                    ...
                }
            max_insights: Maximum number of insights to return (default: 5)
            
        Returns:
            List of Insight objects, prioritized by lowest scores
        """
        # Rank categories by score (lowest first)
        ranked_categories = self._rank_categories(category_scores)
        
        # Generate insights for top categories
        insights = []
        for category_name, score_data in ranked_categories[:max_insights]:
            status_level = score_data["status_level"]
            insight_text = self.insights_matrix.get(category_name, {}).get(status_level)
            
            if insight_text:
                insights.append(Insight(
                    category=category_name,
                    status_level=status_level,
                    text=insight_text,
                    priority=self.category_priority.get(category_name, 99)
                ))
        
        return insights
    
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
        status_level: str
    ) -> str:
        """
        Get specific insight for a category and status level.
        
        Args:
            category: Category name
            status_level: "at_risk", "good", or "excellent"
            
        Returns:
            Insight text
        """
        return self.insights_matrix.get(category, {}).get(status_level, "")


def generate_insights(
    category_scores: Dict[str, Dict],
    max_insights: int = 5
) -> List[Dict]:
    """
    Convenience function to generate insights.
    
    Args:
        category_scores: Category scores from scoring engine
        max_insights: Maximum insights to return
        
    Returns:
        List of insight dictionaries
    """
    engine = InsightsEngine()
    insights = engine.get_insights(category_scores, max_insights)
    
    return [
        {
            "category": insight.category,
            "status_level": insight.status_level,
            "text": insight.text,
            "priority": insight.priority
        }
        for insight in insights
    ]
