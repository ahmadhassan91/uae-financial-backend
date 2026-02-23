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
    text_ar: str  # Arabic translation
    priority: int  # Lower number = higher priority


# Bilingual Insights Matrix (6 categories × 3 status levels)
# Each insight now contains both English (en) and Arabic (ar) translations
# Conditional logic based on design specifications:
# - Income > 30K: income ranges "30,000 to 40,000", "40,000 to 50,000", "50,000 to 100,000", "Above 100,000"
# - Income < 30K: income ranges "Below 5,000", "5,000 to 10,000", "10,000 to 20,000", "20,000 to 30,000"
# - Children = 0: no children
# - Children > 0: has children (1, 2, 3, 4, 5+)
# - Emirati & Woman: nationality = "Emirati" AND gender = "Female"
# - "Else": general fallback
INSIGHTS_MATRIX = {
    "Income Stream": {
        "at_risk": {
            "income_above_30k": {
                "en": "Your income sources seem limited or inconsistent. Focus on creating stability by building a consistent income stream and a small safety buffer with our regular saving plans.",
                "ar": "يبدو أن مصادر دخلكم محدودة أو غير مستقرة. ركزوا على خلق الاستقرار عبر بناء تدفق دخل ثابت من خلال خطط الادخار المنتظمة."
            },
            "default": {
                "en": "Your income sources seem limited or inconsistent. Focus on creating stability by building a consistent income stream and a small safety buffer with our regular saving plans starting with AED 100.",
                "ar": "يبدو أن مصادر دخلكم محدودة أو غير مستقرة. ركزوا على خلق الاستقرار عبر بناء تدفق دخل ثابت من خلال خطط ادخار منتظمة تبدأ من 100 درهم."
            }
        },
        "good": {
            "income_above_30k": {
                "en": "Your income is steady but could be diversified. Explore additional or passive income sources such as our Second Salary Plan or My Million plan, to strengthen financial resilience.",
                "ar": "دخلكم ثابت ولكن يمكن تنويعه. تعرفوا على مصادر دخل إضافية مثل خطة الراتب الإضافي أو خطة My Million لتعزيز المرونة المالية."
            },
            "default": {
                "en": "Your income is steady but could be diversified. Explore additional or passive income sources to strengthen financial resilience.",
                "ar": "دخلكم ثابت ولكن يمكن تنويعه. تعرفوا على مصادر دخل إضافية أو سلبية لتعزيز المرونة المالية."
            }
        },
        "excellent": {
            "income_above_30k": {
                "en": "You have a stable, consistent income. Now focus on long-term growth and wealth accumulation through My Million plan.",
                "ar": "لديكم دخل ثابت ومستمر. ركزوا الآن على النمو طويل الأجل وتراكم الثروة من خلال خطة My Million."
            },
            "default": {
                "en": "You have a stable, consistent income. Focus on long-term growth and wealth-building opportunities. You can utilize our Booster offerings to achieve long-term savings growth.",
                "ar": "لديكم دخل ثابت ومستقر. ركّزوا على فرص النمو طويل الأجل وبناء الثروة. يمكنكم الاستفادة من عروض Booster لدينا لتحقيق نمو مستدام لمدخراتكم على المدى الطويل."
            }
        }
    },
    "Savings Habit": {
        "at_risk": {
            "income_below_30k": {
                "en": "Your savings habits are irregular or minimal. Start small with automated monthly contributions to build consistency and discipline through myPlan.",
                "ar": "عادات الادخار لديكم غير منتظمة أو ضئيلة. ابدؤوا بمساهمات شهرية تلقائية صغيرة لتعزيز الاستمرارية والانضباط من خلال خطة myPlan."
            },
            "income_above_30k": {
                "en": "Your savings habit seems irregular or minimal. Increase your savings safety net with Saving Bonds.",
                "ar": "يبدو أن عادة الادخار لديكم غير منتظمة أو ضئيلة. زيدوا من شبكة الأمان الادخارية الخاصة بكم مع صكوك الادخار."
            },
            "default": {
                "en": "Your savings habits are irregular or minimal. Start small with automated monthly contributions to build consistency and discipline through myPlan.",
                "ar": "عادات الادخار لديكم غير منتظمة أو ضئيلة. ابدؤوا بمساهمات شهرية تلقائية صغيرة لتعزيز الاستمرارية والانضباط من خلال خطة myPlan."
            }
        },
        "good": {
            "default": {
                "en": "You save occasionally, but your savings rate could improve. Set clear goals and increase your savings percentage gradually.",
                "ar": "تدخرون بشكل متقطع، لكن نسبة الادخار لديكم يمكن تحسينها. حددوا أهدافًا واضحة وزيدوا نسبة الادخار تدريجيًا."
            }
        },
        "excellent": {
            "default": {
                "en": "You maintain a strong savings routine. Continue optimizing returns through structured plans and smart investments.",
                "ar": "تحافظون على روتين ادخار قوي. استمروا في تحسين العوائد من خلال الخطط المنظمة والاستثمارات الذكية."
            }
        }
    },
    "Emergency Savings": {
        "at_risk": {
            "default": {
                "en": "You may not have enough set aside for unexpected expenses. Aim for at least 3 months of essential living costs with myPlan.",
                "ar": "قد لا تكون لديكم مدخرات كافية للطوارئ. استهدفوا توفير ما لا يقل عن 3 أشهر من تكاليف المعيشة الأساسية مع خطة myPlan."
            }
        },
        "good": {
            "emirati_woman": {
                "en": "You've built a partial safety net. Keep growing it to cover 6 months of living expenses. Enhance your emergency savings with Ahed savings plan.",
                "ar": "لقد بنيتم شبكة أمان جزئية. استمروا في تنميتها لتغطية 6 أشهر من نفقات المعيشة، وعززوا مدخرات الطوارئ مع خطة عهد."
            },
            "else": {
                "en": "You've built a partial safety net. Keep growing it to cover 6 months of living expenses. Enhance your emergency savings with our myPlan monthly savings plan.",
                "ar": "لقد بنيتم شبكة أمان جزئية. واصلوا في تنميتها لتغطية 6 أشهر من نفقات المعيشة. عزّزوا مدخرات الطوارئ لديكم مع خطة الادخار الشهرية myPlan."
            },
            "default": {
                "en": "You've built a partial safety net. Keep growing it to cover 6 months of living expenses. Enhance your emergency savings with our myPlan monthly savings plan.",
                "ar": "لقد بنيتم شبكة أمان جزئية. واصلوا في تنميتها لتغطية 6 أشهر من نفقات المعيشة. عزّزوا مدخرات الطوارئ لديكم مع خطة الادخار الشهرية myPlan."
            }
        },
        "excellent": {
            "default": {
                "en": "You're well-prepared for emergencies. Consider investing your surplus for long-term sustainable growth. Our Term Sukuk offering provides flexible duration with monthly and quarterly profit payout option.",
                "ar": "أنتم على استعداد جيد لمواجهة الطوارئ. فكّروا في استثمار الفائض لديكم لتحقيق نمو مستدام على المدى الطويل. يمنحكم Term Sukuk مددًا مرنة مع خيار توزيع العوائد شهريًا أو ربع سنويًا."
            }
        }
    },
    "Debt Management": {
        "at_risk": {
            "default": {
                "en": "High debt levels or repayment habits may limit your financial flexibility. Focus on reducing debt and avoiding new obligations.",
                "ar": "قد تحد مستويات الديون المرتفعة أو عادات السداد من مرونتكم المالية. ركزوا على تقليل الديون وتجنب الالتزامات الجديدة."
            }
        },
        "good": {
            "default": {
                "en": "You're managing debt reasonably well, but there's room for improvement. Prioritize timely payments and reduction strategies.",
                "ar": "تديرون الديون بشكل جيد نسبيًا، لكن لا يزال هناك مجال للتحسين. أعطوا الأولوية للسداد المنتظم واستراتيجيات تقليل الديون."
            }
        },
        "excellent": {
            "default": {
                "en": "You maintain excellent control over your debt. Use credit strategically to strengthen your financial profile.",
                "ar": "تحافظون على سيطرة ممتازة على ديونكم. استخدموا الائتمان بشكل استراتيجي لتعزيز ملفكم المالي."
            }
        }
    },
    "Retirement Planning": {
        "at_risk": {
            "default": {
                "en": "You haven't started preparing for retirement yet. Starting early, even with small contributions, can make a big difference.",
                "ar": "لم تبدأوا بعد في التخطيط للتقاعد. البدء مبكرًا، حتى بمساهمات صغيرة، يمكن أن يحدث فرقًا كبيرًا."
            }
        },
        "good": {
            "default": {
                "en": "You've started saving for retirement, but increasing contributions gradually can help you reach your goals faster.",
                "ar": "بدأتم الادخار للتقاعد، لكن زيادة المساهمات تدريجيًا ستساعدكم على تحقيق أهدافكم بشكل أسرع."
            }
        },
        "excellent": {
            "default": {
                "en": "You're actively preparing for retirement. Keep your portfolio balanced to support both income and lifestyle needs.",
                "ar": "أنتم تستعدّون جيدًا للتقاعد. حافظوا على توازن محافظكم لتلبية احتياجات الدخل ونمط الحياة."
            }
        }
    },
    "Protecting Your Family": {
        "at_risk": {
            "default": {
                "en": "Your family may not yet have full financial protection. Explore plans that provide security and peace of mind.",
                "ar": "ربما لا تتمتع عائلتكم بحماية مالية كاملة بعد. تعرّفوا على الخطط التي توفر الأمان وراحة البال."
            }
        },
        "good": {
            "children_above_zero": {
                "en": "You have some coverage, but it may not be sufficient. Review your plans and consider saving for your child's education with My Education Plan.",
                "ar": "لديكم بعض المدخرات، لكنها قد لا تكون كافية. راجعوا خططكم وفكّروا في الادخار لتعليم طفلكم مع خطة تعليمي."
            },
            "children_zero": {
                "en": "You have basic financial protection in place, but coverage may be limited. Our Second Salary monthly plan offers flexible and defined duration to achieve your secondary income goals.",
                "ar": "لديكم حماية مالية أساسية، لكنها قد تكون محدودة. يقدّم برنامج الراتب الإضافي مدة محددة ومرنة لمساعدتكم على تحقيق دخل إضافي في المستقبل."
            },
            "default": {
                "en": "You have basic financial protection in place, but coverage may be limited. Our Second Salary monthly plan offers flexible and defined duration to achieve your secondary income goals.",
                "ar": "لديكم حماية مالية أساسية، لكنها قد تكون محدودة. يقدّم برنامج الراتب الإضافي مدة محددة ومرنة لمساعدتكم على تحقيق دخل إضافي في المستقبل."
            }
        },
        "excellent": {
            "default": {
                "en": "You have strong financial protection in place. Keep it updated as your family’s needs evolve.",
                "ar": "لديكم حماية مالية قوية. حافظوا على تحديثها مع تطور احتياجات عائلتكم."
            }
        }
    }
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
            
            # Get conditional insight text based on profile (bilingual)
            insight_texts = self._select_insight_text(
                category_name,
                status_level,
                profile or {}
            )
            
            if insight_texts:
                insights.append(Insight(
                    category=category_name,
                    status_level=status_level,
                    text=insight_texts.get("en", ""),
                    text_ar=insight_texts.get("ar", ""),
                    priority=self.category_priority.get(category_name, 99)
                ))
        
        return insights
    
    def _select_insight_text(
        self,
        category: str,
        status_level: str,
        profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Select appropriate insight text based on profile conditions.
        Returns bilingual dictionary with 'en' and 'ar' keys.
        
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
            Dictionary with 'en' and 'ar' translations
        """
        category_insights = self.insights_matrix.get(category, {})
        status_insights = category_insights.get(status_level, {})
        
        if not status_insights:
            return {"en": "", "ar": ""}
        
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
        return status_insights.get("default", {"en": "", "ar": ""})
    
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
        Ties are broken using CATEGORY_PRIORITY (lower priority number = higher priority).
        
        Categories with lowest scores (1 is lowest on 1-5 scale) indicate areas needing most attention.
        For same scores, the predefined priority hierarchy determines the order.
        
        Args:
            category_scores: Category scores dictionary
            
        Returns:
            List of (category_name, score_data) tuples, sorted by score then priority
        """
        # Convert to list of tuples
        category_list = list(category_scores.items())
        
        # Sort by:
        # 1. Score (ascending - lowest first, as lower scores need more attention)
        # 2. Priority (ascending - lower priority number = higher priority for tie-breaking)
        sorted_categories = sorted(
            category_list,
            key=lambda x: (
                x[1].get("score", 0),  # Lower score = needs more attention
                self.category_priority.get(x[0], 99)  # Lower priority number = higher priority
            )
        )
        
        return sorted_categories
    
    def get_insight_for_category(
        self,
        category: str,
        status_level: str,
        profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Get specific insight for a category and status level with profile conditions.
        Returns bilingual dictionary.
        
        Args:
            category: Category name
            status_level: "at_risk", "good", or "excellent"
            profile: Optional profile data for conditional insights
            
        Returns:
            Dictionary with 'en' and 'ar' translations
        """
        return self._select_insight_text(category, status_level, profile or {})


def generate_insights(
    category_scores: Dict[str, Dict],
    profile: Optional[Dict[str, Any]] = None,
    max_insights: int = 5
) -> List[Dict]:
    """
    Convenience function to generate insights with profile data.
    Returns bilingual insights.
    
    Args:
        category_scores: Category scores from scoring engine
        profile: Optional profile data for conditional insights
        max_insights: Maximum insights to return (strictly enforced at 5)
        
    Returns:
        List of insight dictionaries with both 'text' (English) and 'text_ar' (Arabic)
    """
    engine = InsightsEngine()
    insights = engine.get_insights(category_scores, profile, max_insights)
    
    return [
        {
            "category": insight.category,
            "status_level": insight.status_level,
            "text": insight.text,
            "text_ar": insight.text_ar,
            "priority": insight.priority
        }
        for insight in insights
    ]
