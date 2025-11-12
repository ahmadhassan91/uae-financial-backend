"""
Financial Clinic Survey Questions
6 Categories, 15 Questions, 0-100 Scoring System

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
            FinancialClinicOption(value=5, label_en="My monthly expenses are always below my budget", label_ar="نفقاتي الشهرية دائماً أقل من ميزانيتي"),
            FinancialClinicOption(value=4, label_en="I stay as within my budget every month", label_ar="أبقى ضمن ميزانيتي كل شهر"),
            FinancialClinicOption(value=3, label_en="My budget stays on track on most months", label_ar="ميزانيتي تسير على المسار الصحيح في معظم الأشهر"),
            FinancialClinicOption(value=2, label_en="I usually go over budget with my spending", label_ar="عادةً ما أتجاوز الميزانية مع إنفاقي"),
            FinancialClinicOption(value=1, label_en="I am unable to manage my monthly expenses", label_ar="أنا غير قادر على إدارة نفقاتي الشهرية"),
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
            FinancialClinicOption(value=5, label_en="I have multiple & consistent income streams", label_ar="لدي مصادر دخل متعددة ومتسقة"),
            FinancialClinicOption(value=4, label_en="I have additional income but they are not consistent", label_ar="لدي دخل إضافي ولكن ليس متسقاً"),
            FinancialClinicOption(value=3, label_en="I have only 1 stream of consistent income", label_ar="لدي مصدر دخل واحد فقط متسق"),
            FinancialClinicOption(value=2, label_en="I have only 1 stream of income and it is not consistent", label_ar="لدي مصدر دخل واحد فقط وليس متسقاً"),
            FinancialClinicOption(value=1, label_en="I currently have no income stream", label_ar="ليس لدي حالياً أي مصدر دخل"),
        ]
    ),
    
    # ==================== SAVINGS HABIT (Q3-Q5) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q3",
        number=3,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=10,  # 10% of total score
        text_en="How much of your total income are you able to save every month?",
        text_ar="ما مقدار إجمالي دخلك الذي تستطيع ادخاره كل شهر؟",
        options=[
            FinancialClinicOption(value=5, label_en="More than 20% of my income", label_ar="أكثر من 20٪ من دخلي"),
            FinancialClinicOption(value=4, label_en="15% to 20% of my income", label_ar="15٪ إلى 20٪ من دخلي"),
            FinancialClinicOption(value=3, label_en="5% to 15% of my income", label_ar="5٪ إلى 15٪ من دخلي"),
            FinancialClinicOption(value=2, label_en="Up to 5% of my income", label_ar="ما يصل إلى 5٪ من دخلي"),
            FinancialClinicOption(value=1, label_en="I am not able to save from my income", label_ar="لا أستطيع الادخار من دخلي"),
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
            FinancialClinicOption(value=5, label_en="I primarily save and invest for long-term goals (over 3 years)", label_ar="أدخر وأستثمر بشكل أساسي لأهداف طويلة الأجل (أكثر من 3 سنوات)"),
            FinancialClinicOption(value=4, label_en="I save for medium-term goals (1-3 years)", label_ar="أدخر لأهداف متوسطة الأجل (1-3 سنوات)"),
            FinancialClinicOption(value=3, label_en="I save for both short- and long-term goals", label_ar="أدخر لأهداف قصيرة وطويلة الأجل"),
            FinancialClinicOption(value=2, label_en="I save for short-term goals (less than 1 year)", label_ar="أدخر لأهداف قصيرة الأجل (أقل من سنة واحدة)"),
            FinancialClinicOption(value=1, label_en="I usually save only for immediate needs or emergencies", label_ar="عادةً أدخر فقط للاحتياجات الفورية أو حالات الطوارئ"),
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
            FinancialClinicOption(value=5, label_en="My spending remains the same", label_ar="إنفاقي يبقى كما هو"),
            FinancialClinicOption(value=4, label_en="My spending increases slightly", label_ar="إنفاقي يزداد قليلاً"),
            FinancialClinicOption(value=3, label_en="My spending increase is the same as my income increase", label_ar="زيادة إنفاقي تساوي زيادة دخلي"),
            FinancialClinicOption(value=2, label_en="My spending increase is slightly higher than my income increase", label_ar="زيادة إنفاقي أعلى قليلاً من زيادة دخلي"),
            FinancialClinicOption(value=1, label_en="My spending is much higher than my income increase", label_ar="إنفاقي أعلى بكثير من زيادة دخلي"),
        ]
    ),
    
    # ==================== EMERGENCY SAVINGS (Q6-Q8) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q6",
        number=6,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=5,  # 5% of total score
        text_en="Are you actively saving in an emergency fund?",
        text_ar="هل تدخر بنشاط في صندوق الطوارئ؟",
        options=[
            FinancialClinicOption(value=5, label_en="I already have a sufficient emergency fund", label_ar="لدي بالفعل صندوق طوارئ كافٍ"),
            FinancialClinicOption(value=4, label_en="I save every month towards my emergency fund", label_ar="أدخر كل شهر لصندوق الطوارئ الخاص بي"),
            FinancialClinicOption(value=3, label_en="I try to save consistently but not every month", label_ar="أحاول الادخار بانتظام لكن ليس كل شهر"),
            FinancialClinicOption(value=2, label_en="I save when I can but not consistently", label_ar="أدخر عندما أستطيع ولكن ليس بشكل منتظم"),
            FinancialClinicOption(value=1, label_en="One day I will start saving", label_ar="يوماً ما سأبدأ في الادخار"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q7",
        number=7,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=10,  # 10% of total score (UPDATED from 5%)
        text_en="Do you have enough emergency savings that can cover your basic expenses?",
        text_ar="هل لديك مدخرات طوارئ كافية يمكن أن تغطي نفقاتك الأساسية؟",
        options=[
            FinancialClinicOption(value=5, label_en="I can cover more than 6 months of my expenses", label_ar="أستطيع تغطية أكثر من 6 أشهر من نفقاتي"),
            FinancialClinicOption(value=4, label_en="I can cover 5 to 6 months of my expenses", label_ar="أستطيع تغطية 5 إلى 6 أشهر من نفقاتي"),
            FinancialClinicOption(value=3, label_en="I can cover 3 to 4 months of my expenses", label_ar="أستطيع تغطية 3 إلى 4 أشهر من نفقاتي"),
            FinancialClinicOption(value=2, label_en="I can cover up to 3 months of my expenses", label_ar="أستطيع تغطية ما يصل إلى 3 أشهر من نفقاتي"),
            FinancialClinicOption(value=1, label_en="I cannot cover my expenses", label_ar="لا أستطيع تغطية نفقاتي"),
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
            FinancialClinicOption(value=5, label_en="In my savings or current bank account", label_ar="في حساب التوفير أو الحساب الجاري الخاص بي"),
            FinancialClinicOption(value=4, label_en="In term or fixed deposits", label_ar="في ودائع لأجل أو ثابتة"),
            FinancialClinicOption(value=3, label_en="In my investment account", label_ar="في حساب الاستثمار الخاص بي"),
            FinancialClinicOption(value=2, label_en="In the form of assets/commodities (gold/silver etc.)", label_ar="في شكل أصول/سلع (ذهب/فضة إلخ)"),
            FinancialClinicOption(value=1, label_en="I do not have emergency savings", label_ar="ليس لدي مدخرات طوارئ"),
        ]
    ),
    
    # ==================== DEBT MANAGEMENT (Q9-Q10) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q9",
        number=9,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=10,  # 10% of total score
        text_en="How often are you able to pay your bills and loan installments on time?",
        text_ar="كم مرة تستطيع دفع فواتيرك وأقساط القروض في الوقت المحدد؟",
        options=[
            FinancialClinicOption(value=5, label_en="I make my payments every month", label_ar="أقوم بدفع مستحقاتي كل شهر"),
            FinancialClinicOption(value=4, label_en="I make my monthly payments but not consistently", label_ar="أقوم بدفع مستحقاتي الشهرية ولكن ليس بشكل منتظم"),
            FinancialClinicOption(value=3, label_en="I occasionally make my monthly payments", label_ar="أحياناً أقوم بدفع مستحقاتي الشهرية"),
            FinancialClinicOption(value=2, label_en="I miss most of my monthly payments", label_ar="أفوت معظم مدفوعاتي الشهرية"),
            FinancialClinicOption(value=1, label_en="I am not able to make my monthly payments", label_ar="لا أستطيع دفع مستحقاتي الشهرية"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q10",
        number=10,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=5,  # 5% of total score
        text_en="What percentage of monthly income goes to debt payments?",
        text_ar="ما هي النسبة المئوية من الدخل الشهري التي تذهب لسداد الديون؟",
        options=[
            FinancialClinicOption(value=5, label_en="I have no debt", label_ar="ليس لدي ديون"),
            FinancialClinicOption(value=4, label_en="Less than 20% of my monthly income", label_ar="أقل من 20٪ من دخلي الشهري"),
            FinancialClinicOption(value=3, label_en="Less than 35% of my monthly income", label_ar="أقل من 35٪ من دخلي الشهري"),
            FinancialClinicOption(value=2, label_en="Less than 50% of my monthly income", label_ar="أقل من 50٪ من دخلي الشهري"),
            FinancialClinicOption(value=1, label_en="More than 50% of my monthly income", label_ar="أكثر من 50٪ من دخلي الشهري"),
        ]
    ),
    
    # ==================== RETIREMENT PLANNING (Q11-Q13) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q11",
        number=11,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=5,  # 5% of total score
        text_en="Are you actively saving or investing for retirement?",
        text_ar="هل تدخر أو تستثمر بنشاط للتقاعد؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, contributing regularly for a retirement plan and with a stable plan", label_ar="نعم، أساهم بانتظام في خطة تقاعد ولدي خطة مستقرة"),
            FinancialClinicOption(value=4, label_en="Yes, I save for retirement occasionally, but my contributions vary depending on my monthly expenses", label_ar="نعم، أدخر للتقاعد أحياناً، لكن مساهماتي تتفاوت حسب نفقاتي الشهرية"),
            FinancialClinicOption(value=3, label_en="I have started saving or investing for retirement, but I don't have a clear plan or specific goal", label_ar="بدأت في الادخار أو الاستثمار للتقاعد، لكن ليس لدي خطة واضحة أو هدف محدد"),
            FinancialClinicOption(value=2, label_en="Yes, but I save whenever I can and without a clear plan", label_ar="نعم، لكنني أدخر متى استطعت وبدون خطة واضحة"),
            FinancialClinicOption(value=1, label_en="No, I have not thought about saving for retirement", label_ar="لا، لم أفكر في الادخار للتقاعد"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q12",
        number=12,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=10,  # 10% of total score
        text_en="How confident do you feel about maintaining a comfortable lifestyle after retirement?",
        text_ar="ما مدى ثقتك في الحفاظ على نمط حياة مريح بعد التقاعد؟",
        options=[
            FinancialClinicOption(value=5, label_en="I have already secured a retirement income", label_ar="لقد أمّنت بالفعل دخلاً للتقاعد"),
            FinancialClinicOption(value=4, label_en="I am highly confident of having a stable income after retirement", label_ar="أنا واثق جداً من الحصول على دخل مستقر بعد التقاعد"),
            FinancialClinicOption(value=3, label_en="I am somewhat confident of having a stable income after retirement", label_ar="أنا واثق إلى حد ما من الحصول على دخل مستقر بعد التقاعد"),
            FinancialClinicOption(value=2, label_en="I am not very confident of having a stable income after retirement", label_ar="لست واثقاً جداً من الحصول على دخل مستقر بعد التقاعد"),
            FinancialClinicOption(value=1, label_en="I am certain I will not have a stable income after retirement", label_ar="أنا متأكد أنني لن أحصل على دخل مستقر بعد التقاعد"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q13",
        number=13,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=5,  # 5% of total score
        text_en="How much of your current income will you be able to cover after your retirement?",
        text_ar="ما مقدار دخلك الحالي الذي ستتمكن من تغطيته بعد تقاعدك؟",
        options=[
            FinancialClinicOption(value=5, label_en="My retirement income will be able to provide more than 80% of my current income", label_ar="سيتمكن دخل التقاعد من توفير أكثر من 80٪ من دخلي الحالي"),
            FinancialClinicOption(value=4, label_en="My retirement income will be able to provide 50% to 80% of my current income", label_ar="سيتمكن دخل التقاعد من توفير 50٪ إلى 80٪ من دخلي الحالي"),
            FinancialClinicOption(value=3, label_en="My retirement income will be able to provide 20% to 50% of my current income", label_ar="سيتمكن دخل التقاعد من توفير 20٪ إلى 50٪ من دخلي الحالي"),
            FinancialClinicOption(value=2, label_en="My retirement income will be able to provide up to 20% of my current income", label_ar="سيتمكن دخل التقاعد من توفير ما يصل إلى 20٪ من دخلي الحالي"),
            FinancialClinicOption(value=1, label_en="I am certain I will not have a stable income after retirement", label_ar="أنا متأكد أنني لن أحصل على دخل مستقر بعد التقاعد"),
        ]
    ),
    
    # ==================== PROTECTING YOUR FAMILY (Q14-Q15) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q14",
        number=14,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Do you have adequate life Takaful/Insurance coverage?",
        text_ar="هل لديك تغطية تكافل/تأمين على الحياة كافية؟",
        options=[
            FinancialClinicOption(value=5, label_en="I have sufficient coverage to cover 12 months of my income", label_ar="لدي تغطية كافية لتغطية 12 شهراً من دخلي"),
            FinancialClinicOption(value=4, label_en="I have sufficient coverage to cover up to 11 months of my income", label_ar="لدي تغطية كافية لتغطية ما يصل إلى 11 شهراً من دخلي"),
            FinancialClinicOption(value=3, label_en="I have enough coverage to cover up to 5 months of my income", label_ar="لدي تغطية كافية لتغطية ما يصل إلى 5 أشهر من دخلي"),
            FinancialClinicOption(value=2, label_en="I have enough coverage for up to 3 months of my income", label_ar="لدي تغطية كافية لما يصل إلى 3 أشهر من دخلي"),
            FinancialClinicOption(value=1, label_en="I do not have any coverage", label_ar="ليس لدي أي تغطية"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q15",
        number=15,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Are you actively saving for education savings for your children?",
        text_ar="هل تدخر بنشاط لمدخرات تعليم أطفالك؟",
        options=[
            FinancialClinicOption(value=5, label_en="I don't have any need to save for my children's education", label_ar="ليس لدي أي حاجة للادخار لتعليم أطفالي"),
            FinancialClinicOption(value=4, label_en="Yes, I have sufficient funds for my children's education", label_ar="نعم، لدي أموال كافية لتعليم أطفالي"),
            FinancialClinicOption(value=3, label_en="Yes, I am saving towards having a sufficient education fund", label_ar="نعم، أدخر نحو الحصول على صندوق تعليم كافٍ"),
            FinancialClinicOption(value=2, label_en="Yes, but I am starting to save for an education fund", label_ar="نعم، لكنني بدأت في الادخار لصندوق تعليم"),
            FinancialClinicOption(value=1, label_en="Yes, but I do not have any education saving for my children", label_ar="نعم، لكن ليس لدي أي مدخرات تعليمية لأطفالي"),
        ],
        conditional=True,
        condition_field="children",
        condition_value=1  # Show if children > 0 (any value >= 1 means has children)
    ),
]


# Category weights (must sum to 100%)
CATEGORY_WEIGHTS = {
    FinancialClinicCategory.INCOME_STREAM: 15,      # Q1: 5% + Q2: 10%
    FinancialClinicCategory.SAVINGS_HABIT: 20,      # Q3: 10% + Q4: 5% + Q5: 5%
    FinancialClinicCategory.EMERGENCY_SAVINGS: 20,  # Q6: 5% + Q7: 10% + Q8: 5%
    FinancialClinicCategory.DEBT_MANAGEMENT: 15,    # Q9: 10% + Q10: 5%
    FinancialClinicCategory.RETIREMENT_PLANNING: 20, # Q11: 5% + Q12: 10% + Q13: 5%
    FinancialClinicCategory.PROTECTING_FAMILY: 10,  # Q14: 5% + Q15: 5%
}


def get_questions_for_profile(children_count: int = 0) -> List[FinancialClinicQuestion]:
    """
    Get Financial Clinic questions based on profile.
    
    Args:
        children_count: Number of children (0 = no children, >= 1 = has children)
        
    Returns:
        14 or 15 questions depending on children status:
        - If children_count = 0: Returns 14 questions (Q15 excluded)
        - If children_count > 0: Returns all 15 questions (Q15 included)
    """
    if children_count > 0:
        # Has children: show all 15 questions including Q15
        return FINANCIAL_CLINIC_QUESTIONS
    else:
        # No children: exclude Q15
        return [q for q in FINANCIAL_CLINIC_QUESTIONS if q.id != "fc_q15"]


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
