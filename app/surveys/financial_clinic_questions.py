"""
Financial Clinic Survey Questions
6 Categories, 16 Questions, 0-100 Scoring System

This module defines the complete Financial Clinic question set as specified
in the client requirements. This represents a complete replacement of the 
original 7-pillar system.

Key Differences from Original:
- 6 categories (not 7)
- 0-100 score range (not 15-75)
- Different question wording and structure
- New weighted distribution
- Product recommendation integration
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class FinancialClinicCategory(str, Enum):
    """Financial Clinic categories (6 total)."""
    INCOME_STREAM = "Income Stream"
    SAVINGS_HABIT = "Savings Habit"
    EMERGENCY_SAVINGS = "Emergency Savings"
    DEBT_MANAGEMENT = "Debt Management"
    RETIREMENT_PLANNING = "Retirement Planning"
    PROTECTING_FAMILY = "Protecting Your Family"


@dataclass
class FinancialClinicOption:
    """Survey answer option with point value."""
    value: int  # 1-5 points (5 = best answer)
    label_en: str
    label_ar: str = "[Translation needed]"


@dataclass
class FinancialClinicQuestion:
    """Financial Clinic question definition."""
    id: str
    number: int
    category: FinancialClinicCategory
    weight: int  # Percentage weight in category
    text_en: str
    text_ar: str
    options: List[FinancialClinicOption]
    conditional: bool = False
    condition_field: Optional[str] = None
    condition_value: Optional[Any] = None


# Financial Clinic Questions - Complete Set (16 Questions)
FINANCIAL_CLINIC_QUESTIONS: List[FinancialClinicQuestion] = [
    # ==================== INCOME STREAM (Q1-Q2) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q1",
        number=1,
        category=FinancialClinicCategory.INCOME_STREAM,
        weight=5,  # 5% of total score
        text_en="How well are you managing your household monthly expenses?",
        text_ar="ما مدى نجاحك في إدارة نفقاتك الشهرية المنزلية؟",
        options=[
            FinancialClinicOption(value=5, label_en="Very well", label_ar="جيد جداً"),
            FinancialClinicOption(value=4, label_en="Well", label_ar="جيد"),
            FinancialClinicOption(value=3, label_en="Moderately", label_ar="معتدل"),
            FinancialClinicOption(value=2, label_en="Poorly", label_ar="ضعيف"),
            FinancialClinicOption(value=1, label_en="Very poorly", label_ar="ضعيف جداً"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q2",
        number=2,
        category=FinancialClinicCategory.INCOME_STREAM,
        weight=10,  # 10% of total score
        text_en="Do you have more than one source of income?",
        text_ar="هل لديك أكثر من مصدر دخل؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, multiple sources", label_ar="نعم، مصادر متعددة"),
            FinancialClinicOption(value=4, label_en="Yes, one additional", label_ar="نعم، مصدر إضافي واحد"),
            FinancialClinicOption(value=3, label_en="No, but planning to", label_ar="لا، ولكن أخطط لذلك"),
            FinancialClinicOption(value=2, label_en="No, not planning", label_ar="لا، ولا أخطط"),
            FinancialClinicOption(value=1, label_en="No, don't need to", label_ar="لا، ولا أحتاج"),
        ]
    ),
    
    # ==================== SAVINGS HABIT (Q3-Q5) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q3",
        number=3,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=10,  # 10% of total score
        text_en="How much of your income are you able to save every month?",
        text_ar="ما مقدار دخلك الذي تستطيع ادخاره كل شهر؟",
        options=[
            FinancialClinicOption(value=5, label_en="20% or more", label_ar="20٪ أو أكثر"),
            FinancialClinicOption(value=4, label_en="15-20%", label_ar="15-20٪"),
            FinancialClinicOption(value=3, label_en="10-15%", label_ar="10-15٪"),
            FinancialClinicOption(value=2, label_en="5-10%", label_ar="5-10٪"),
            FinancialClinicOption(value=1, label_en="Less than 5%", label_ar="أقل من 5٪"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q4",
        number=4,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=5,  # 5% of total score
        text_en="What is the typical duration of your savings goals?",
        text_ar="ما هي المدة النموذجية لأهداف الادخار الخاصة بك؟",
        options=[
            FinancialClinicOption(value=5, label_en="Long term (5+ years)", label_ar="طويلة الأجل (5+ سنوات)"),
            FinancialClinicOption(value=4, label_en="Medium term (3-5 years)", label_ar="متوسطة الأجل (3-5 سنوات)"),
            FinancialClinicOption(value=3, label_en="Short term (1-3 years)", label_ar="قصيرة الأجل (1-3 سنوات)"),
            FinancialClinicOption(value=2, label_en="Irregular", label_ar="غير منتظمة"),
            FinancialClinicOption(value=1, label_en="No savings plan", label_ar="لا توجد خطة ادخار"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q5",
        number=5,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=5,  # 5% of total score
        text_en="When your income increases, how does your spending behavior change?",
        text_ar="عندما يزداد دخلك، كيف يتغير سلوك الإنفاق لديك؟",
        options=[
            FinancialClinicOption(value=5, label_en="Save most of it", label_ar="أدخر معظمه"),
            FinancialClinicOption(value=4, label_en="Balance saving and spending", label_ar="أوازن بين الادخار والإنفاق"),
            FinancialClinicOption(value=3, label_en="Spend most of it", label_ar="أنفق معظمه"),
            FinancialClinicOption(value=2, label_en="Spend all of it", label_ar="أنفق كله"),
            FinancialClinicOption(value=1, label_en="Increase debt", label_ar="أزيد من ديوني"),
        ]
    ),
    
    # ==================== EMERGENCY SAVINGS (Q6-Q8) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q6",
        number=6,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=5,  # 5% of total score
        text_en="Are you actively saving for an emergency fund?",
        text_ar="هل تدخر بنشاط لصندوق الطوارئ؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, regularly", label_ar="نعم، بانتظام"),
            FinancialClinicOption(value=4, label_en="Yes, occasionally", label_ar="نعم، أحياناً"),
            FinancialClinicOption(value=3, label_en="Planning to start", label_ar="أخطط للبدء"),
            FinancialClinicOption(value=2, label_en="Not currently", label_ar="ليس حالياً"),
            FinancialClinicOption(value=1, label_en="Not needed", label_ar="غير مطلوب"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q7",
        number=7,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=5,  # 5% of total score
        text_en="Do you have enough emergency savings to cover 6 months of expenses?",
        text_ar="هل لديك مدخرات طوارئ كافية لتغطية نفقات 6 أشهر؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, 6+ months", label_ar="نعم، 6+ أشهر"),
            FinancialClinicOption(value=4, label_en="Yes, 3-6 months", label_ar="نعم، 3-6 أشهر"),
            FinancialClinicOption(value=3, label_en="Yes, 1-3 months", label_ar="نعم، 1-3 أشهر"),
            FinancialClinicOption(value=2, label_en="Less than 1 month", label_ar="أقل من شهر"),
            FinancialClinicOption(value=1, label_en="No emergency fund", label_ar="لا يوجد صندوق طوارئ"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q8",
        number=8,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=5,  # 5% of total score
        text_en="Where do you keep your emergency savings?",
        text_ar="أين تحتفظ بمدخرات الطوارئ الخاصة بك؟",
        options=[
            FinancialClinicOption(value=5, label_en="High-yield savings account", label_ar="حساب توفير عالي العائد"),
            FinancialClinicOption(value=4, label_en="Regular savings account", label_ar="حساب توفير عادي"),
            FinancialClinicOption(value=3, label_en="Investment account", label_ar="حساب استثماري"),
            FinancialClinicOption(value=2, label_en="Cash at home", label_ar="نقداً في المنزل"),
            FinancialClinicOption(value=1, label_en="No emergency fund", label_ar="لا يوجد صندوق طوارئ"),
        ]
    ),
    
    # ==================== DEBT MANAGEMENT (Q9-Q11) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q9",
        number=9,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=10,  # 10% of total score
        text_en="How often are you able to pay bills on time without difficulty?",
        text_ar="كم مرة تستطيع دفع الفواتير في الوقت المحدد دون صعوبة؟",
        options=[
            FinancialClinicOption(value=5, label_en="Always", label_ar="دائماً"),
            FinancialClinicOption(value=4, label_en="Usually", label_ar="عادةً"),
            FinancialClinicOption(value=3, label_en="Sometimes", label_ar="أحياناً"),
            FinancialClinicOption(value=2, label_en="Rarely", label_ar="نادراً"),
            FinancialClinicOption(value=1, label_en="Never", label_ar="أبداً"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q10",
        number=10,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=5,  # 5% of total score
        text_en="What percentage of your monthly income goes to debt payments?",
        text_ar="ما هي النسبة المئوية من دخلك الشهري التي تذهب لسداد الديون؟",
        options=[
            FinancialClinicOption(value=5, label_en="0%", label_ar="0٪"),
            FinancialClinicOption(value=4, label_en="Less than 10%", label_ar="أقل من 10٪"),
            FinancialClinicOption(value=3, label_en="10-20%", label_ar="10-20٪"),
            FinancialClinicOption(value=2, label_en="20-30%", label_ar="20-30٪"),
            FinancialClinicOption(value=1, label_en="30% or more", label_ar="30٪ أو أكثر"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q11",
        number=11,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=5,  # 5% of total score
        text_en="How well do you understand your credit score and its impact?",
        text_ar="ما مدى فهمك لتصنيفك الائتماني وتأثيره؟",
        options=[
            FinancialClinicOption(value=5, label_en="Very well", label_ar="جيد جداً"),
            FinancialClinicOption(value=4, label_en="Well", label_ar="جيد"),
            FinancialClinicOption(value=3, label_en="Somewhat", label_ar="إلى حد ما"),
            FinancialClinicOption(value=2, label_en="Not well", label_ar="ليس جيداً"),
            FinancialClinicOption(value=1, label_en="Not at all", label_ar="لا على الإطلاق"),
        ]
    ),
    
    # ==================== RETIREMENT PLANNING (Q12-Q13) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q12",
        number=12,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=10,  # 10% of total score
        text_en="Are you actively saving for retirement?",
        text_ar="هل تدخر بنشاط للتقاعد؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, actively", label_ar="نعم، بنشاط"),
            FinancialClinicOption(value=4, label_en="Yes, occasionally", label_ar="نعم، أحياناً"),
            FinancialClinicOption(value=3, label_en="Planning to start", label_ar="أخطط للبدء"),
            FinancialClinicOption(value=2, label_en="Not currently", label_ar="ليس حالياً"),
            FinancialClinicOption(value=1, label_en="Not needed", label_ar="غير مطلوب"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q13",
        number=13,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=5,  # 5% of total score
        text_en="How confident are you about maintaining your desired lifestyle in retirement?",
        text_ar="ما مدى ثقتك في الحفاظ على نمط الحياة المطلوب في التقاعد؟",
        options=[
            FinancialClinicOption(value=5, label_en="Very confident", label_ar="واثق جداً"),
            FinancialClinicOption(value=4, label_en="Confident", label_ar="واثق"),
            FinancialClinicOption(value=3, label_en="Somewhat confident", label_ar="واثق إلى حد ما"),
            FinancialClinicOption(value=2, label_en="Not confident", label_ar="غير واثق"),
            FinancialClinicOption(value=1, label_en="Very uncertain", label_ar="غير متأكد جداً"),
        ]
    ),
    
    # ==================== PROTECTING YOUR FAMILY (Q14-Q16) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q14",
        number=14,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Do you have a clear financial plan for the next 3-5 years?",
        text_ar="هل لديك خطة مالية واضحة للسنوات الثلاث إلى الخمس القادمة؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, detailed plan", label_ar="نعم، خطة مفصلة"),
            FinancialClinicOption(value=4, label_en="Yes, general plan", label_ar="نعم، خطة عامة"),
            FinancialClinicOption(value=3, label_en="Rough idea", label_ar="فكرة تقريبية"),
            FinancialClinicOption(value=2, label_en="No plan", label_ar="لا توجد خطة"),
            FinancialClinicOption(value=1, label_en="Don't think about it", label_ar="لا أفكر في ذلك"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q15",
        number=15,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Do you have adequate Takaful (insurance) coverage for yourself and your family?",
        text_ar="هل لديك تغطية تكافل (تأمين) كافية لك ولعائلتك؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, comprehensive", label_ar="نعم، شاملة"),
            FinancialClinicOption(value=4, label_en="Yes, basic", label_ar="نعم، أساسية"),
            FinancialClinicOption(value=3, label_en="Partial coverage", label_ar="تغطية جزئية"),
            FinancialClinicOption(value=2, label_en="No coverage", label_ar="لا توجد تغطية"),
            FinancialClinicOption(value=1, label_en="Not needed", label_ar="غير مطلوب"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q16",
        number=16,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Are you actively saving for education savings for your children?",
        text_ar="هل تدخر بنشاط لمدخرات تعليم أطفالك؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, I have sufficient funds for my children's education", label_ar="نعم، لدي أموال كافية لتعليم أطفالي"),
            FinancialClinicOption(value=4, label_en="Yes, I am saving towards having a sufficient education fund", label_ar="نعم، أدخر للحصول على صندوق تعليم كافٍ"),
            FinancialClinicOption(value=3, label_en="Yes, but I am starting to save for an education fund", label_ar="نعم، لكنني بدأت في الادخار لصندوق التعليم"),
            FinancialClinicOption(value=2, label_en="Yes, but I do not have any education saving for my children", label_ar="نعم، لكن ليس لدي أي مدخرات تعليمية لأطفالي"),
            FinancialClinicOption(value=1, label_en="No, I do not need any education fund (if children is selected >0)", label_ar="لا، لا أحتاج إلى أي صندوق تعليم (إذا تم اختيار الأطفال > 0)"),
        ]
        # Note: No conditional flag - Q16 is shown to everyone
    ),
]


# Category weights (must sum to 100%)
CATEGORY_WEIGHTS = {
    FinancialClinicCategory.INCOME_STREAM: 15,
    FinancialClinicCategory.SAVINGS_HABIT: 20,
    FinancialClinicCategory.EMERGENCY_SAVINGS: 15,
    FinancialClinicCategory.DEBT_MANAGEMENT: 20,
    FinancialClinicCategory.RETIREMENT_PLANNING: 15,
    FinancialClinicCategory.PROTECTING_FAMILY: 15,
}


def get_questions_for_profile(has_children: bool = True) -> List[FinancialClinicQuestion]:
    """
    Get all Financial Clinic questions.
    
    Note: In Financial Clinic v2, ALL 16 questions are always shown.
    Q16 is NOT conditional - it applies to everyone regardless of children status.
    
    Args:
        has_children: Deprecated parameter (kept for API compatibility)
        
    Returns:
        All 16 Financial Clinic questions
    """
    return FINANCIAL_CLINIC_QUESTIONS


def get_question_by_id(question_id: str) -> Optional[FinancialClinicQuestion]:
    """Get a specific question by ID."""
    for question in FINANCIAL_CLINIC_QUESTIONS:
        if question.id == question_id:
            return question
    return None


def get_questions_by_category(category: FinancialClinicCategory) -> List[FinancialClinicQuestion]:
    """Get all questions for a specific category."""
    return [q for q in FINANCIAL_CLINIC_QUESTIONS if q.category == category]


def validate_weights() -> bool:
    """
    Validate that question weights sum to 100%.
    
    Returns:
        True if weights are valid
    """
    total_weight = sum(q.weight for q in FINANCIAL_CLINIC_QUESTIONS)
    return total_weight == 100


# Validate weights on module load
if not validate_weights():
    raise ValueError(
        f"Question weights do not sum to 100%. "
        f"Current total: {sum(q.weight for q in FINANCIAL_CLINIC_QUESTIONS)}%"
    )
