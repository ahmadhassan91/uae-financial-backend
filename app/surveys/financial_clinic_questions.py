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
        text_ar="ما مدى نجاحكم في إدارة نفقات أسرتكم الشهرية؟",
        options=[
              FinancialClinicOption(value=5, label_en="My monthly expenses are always below my budget", label_ar="نفقاتي الشهرية دائماً أقلّ من ميزانيتي"),
              FinancialClinicOption(value=4, label_en="I stay within my budget every month", label_ar="أنا ألتزم بميزانيتي كلّ شهر"),
            FinancialClinicOption(value=3, label_en="My budget stays on track on most months", label_ar="أنا أبقى ضمن حدود ميزانيتي في معظم الأشهر"),
            FinancialClinicOption(value=2, label_en="I usually go over budget with my spending", label_ar="تتجاوز نفقاتي عادة الميزانية المحدّدة"),
            FinancialClinicOption(value=1, label_en="I am unable to manage my monthly expenses", label_ar="أنا عاجز عن إدارة نفقاتي الشهرية"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q2",
        number=2,
        category=FinancialClinicCategory.INCOME_STREAM,
        weight=10,  # 10% of total score
        text_en="Do you have more than one source of income?",
        text_ar="هل لديكم أكثر من مصدر للدخل؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, I have multiple consistent sources of income", label_ar="لديّ موارد متعددة ومنتظمة للدخل"),
            FinancialClinicOption(value=4, label_en="I have additional income but they are not consistent", label_ar="لديّ دخل إضافيّ لكنّه غير منتظم"),
            FinancialClinicOption(value=3, label_en="I have only 1 stream of consistent income", label_ar="لديّ مورد واحد فقط للدخل المنتظم"),
            FinancialClinicOption(value=2, label_en="I have only 1 stream of income and it is not consistent", label_ar="لديّ مورد واحد فقط للدخل، وهو غير منتظم"),
            FinancialClinicOption(value=1, label_en="I currently have no income stream", label_ar="ليس لديّ أيّ مورد للدخل حالياً"),
        ]
    ),
    
    # ==================== SAVINGS HABIT (Q3-Q5) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q3",
        number=3,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=10,  # 10% of total score
        text_en="How much of your total income are you able to save every month?",
        text_ar="ما النسبة التي تستطيعون ادخارها من إجمالي دخلكم شهريًا؟",
        options=[
              FinancialClinicOption(value=5, label_en="More than 20% of my income", label_ar="أكثر من %20 من دخلي"),
               FinancialClinicOption(value=4, label_en="15% to 20% of my income", label_ar="%15 إلى %20 من دخلي"),
            FinancialClinicOption(value=3, label_en="5% to 15% of my income", label_ar="%5 إلى %15 من دخلي"),
            FinancialClinicOption(value=2, label_en="Up to 5% of my income", label_ar="حتى %5 من دخلي"),
            FinancialClinicOption(value=1, label_en="I am not able to save from my income", label_ar="أنا غير قادر على الادخار من دخلي"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q4",
        number=4,
        category=FinancialClinicCategory.SAVINGSF_HABIT,
        weight=5,  # 5% of total score
        text_en="What is the typical duration of your savings goals?",
        text_ar="ما هي المدة المعتادة لتحقيق أهدافكم الادخارية؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I primarily save and invest for long-term goals (over 3 years)", label_ar="أدّخر وأستثمر بشكل أساسي لتحقيق أهداف طويلة الأجل (أكثر من 3 سنوات)"),
                            FinancialClinicOption(value=4, label_en="I save for medium-term goals (1–3 years)", label_ar="أدّخر لتحقيق أهداف متوسّطة الأجل (سنة إلى 3 سنوات)"),
                        FinancialClinicOption(value=3, label_en="I save for both short- and long-term goals", label_ar="أدّخر لتحقيق أهداف قصيرة وطويلة الأجل على حدّ سواء"),
                        FinancialClinicOption(value=2, label_en="I save for short-term goals (less than 1 year)", label_ar="أدّخر لتحقيق أهداف قصيرة الأجل (أقلّ من سنة)"),
                        FinancialClinicOption(value=1, label_en="I usually save only for immediate needs or emergencies", label_ar="عادةً ما أدّخر فقط للاحتياجات العاجلة أو لحالات الطوارئ"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q5",
        number=5,
        category=FinancialClinicCategory.SAVINGS_HABIT,
        weight=5,  # 5% of total score
        text_en="When your income increases, how does your spending behavior change?",
        text_ar="عندما يزداد دخلكم، كيف يتغيّر سلوككم الإنفاقي؟",
        options=[
                            FinancialClinicOption(value=5, label_en="My spending remains the same", label_ar="تبقى نفقاتي ثابتة"),
                            FinancialClinicOption(value=4, label_en="My spending increases slightly", label_ar="تزداد نفقاتي قليلاً"),
                        FinancialClinicOption(value=3, label_en="My spending increase is the same as my income increase", label_ar="تزداد نفقاتي بنفس نسبة زيادة دخلي"),
                        FinancialClinicOption(value=2, label_en="My spending increase is slightly higher than my income increase", label_ar="تزداد نفقاتي بنسبة أعلى بقليل من زيادة دخلي"),
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
        text_ar="هل أنتم ملتزمون بالادخار للطوارئ؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I already have sufficient emergency savings", label_ar="مدخرات الطوارئ الخاصة بي كافية بالفعل"),
                            FinancialClinicOption(value=4, label_en="I save every month towards my emergency savings", label_ar="أدّخر شهريًا في حساب الطوارئ الخاص بي."),
                        FinancialClinicOption(value=3, label_en="I try to save consistently but not every month", label_ar="أحاول أن أدّخر بانتظام، لكن ليس كلّ شهر"),
                        FinancialClinicOption(value=2, label_en="I save when I can but not consistently", label_ar="أدّخر كلّما أمكن، لكن ليس بانتظام"),
                        FinancialClinicOption(value=1, label_en="One day I will start saving", label_ar="سأبدأ بالادخار يوماً ما"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q7",
        number=7,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=10,  # 10% of total score (UPDATED from 5%)
        text_en="Do you have enough emergency savings that can cover your basic expenses?",
        text_ar="هل لديكم مدخرات طوارئ كافية لتغطية نفقاتكم الأساسية؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I can cover more than 6 months of my expenses", label_ar="بإمكاني تحمّل نفقاتي لأكثر من 6 أشهر"),
                            FinancialClinicOption(value=4, label_en="I can cover 5 to 6 months of my expenses", label_ar="بإمكاني تحمّل نفقاتي من 5 إلى 6 أشهر"),
                        FinancialClinicOption(value=3, label_en="I can cover 3 to 4 months of my expenses", label_ar="بإمكاني تحمّل نفقاتي من 3 إلى 4 أشهر"),
                        FinancialClinicOption(value=2, label_en="I can cover up to 3 months of my expenses", label_ar="بإمكاني تحمّل نفقاتي لمدة تصل إلى 3 أشهر"),
                        FinancialClinicOption(value=1, label_en="I cannot cover my expenses", label_ar="لا يمكنني أن أتحمّل نفقاتي"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q8",
        number=8,
        category=FinancialClinicCategory.EMERGENCY_SAVINGS,
        weight=5,  # 5% of total score
        text_en="Where do you keep your emergency savings?",
        text_ar="أين تحتفظون بمدخرات الطوارئ الخاصة بكم؟",
        options=[
                            FinancialClinicOption(value=5, label_en="In Savings Sukuk,  savings or current account", label_ar="في  صكوك الادخار  /حسابي المصرفي، الادخاري أو الجاري"),
                            FinancialClinicOption(value=4, label_en="In term or fixed deposits", label_ar="في ودائع لأجل أو ودائع ثابتة"),
                        FinancialClinicOption(value=3, label_en="In my investment account", label_ar="في حسابي الاستثماري"),
                        FinancialClinicOption(value=2, label_en="In the form of assets/commodities (gold/silver etc.)", label_ar="على شكل أصول/سلع (ذهب/فضة، إلخ.)"),
                        FinancialClinicOption(value=1, label_en="I do not have emergency savings", label_ar="ليس لديّ مدخرات للطوارئ"),
        ]
    ),
    
    # ==================== DEBT MANAGEMENT (Q9-Q10) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q9",
        number=9,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=10,  # 10% of total score
        text_en="How often are you able to pay your bills and loan installments on time?",
        text_ar="بأيّ وتيرة تتمكّنون من دفع الفواتير وأقساط القروض في موعدها؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I make my payments every month", label_ar="أنا أسدّد دفعاتي كلّ شهر"),
                            FinancialClinicOption(value=4, label_en="I make my monthly payments but not consistently", label_ar="أنا أسدّد دفعاتي الشهريّة، لكن ليس بشكل منتظم"),
                        FinancialClinicOption(value=3, label_en="I occasionally make my monthly payments", label_ar="أنا أسدّد دفعاتي الشهريّة في بعض الأحيان"),
                        FinancialClinicOption(value=2, label_en="I miss most of my monthly payments", label_ar="أنا أتخلف عن سداد معظم دفعاتي الشهرية"),
                        FinancialClinicOption(value=1, label_en="I am not able to make my monthly payments", label_ar="أنا عاجز عن سداد دفعاتي الشهريّة"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q10",
        number=10,
        category=FinancialClinicCategory.DEBT_MANAGEMENT,
        weight=5,  # 5% of total score
        text_en="What percentage of monthly income goes to debt payments?",
        text_ar="ما هي النسبة المخصصة لسداد الديون من دخلكم الشهري؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I have no debt", label_ar="ليس لديّ ديون"),
                        FinancialClinicOption(value=4, label_en="Less than 20% of my monthly income", label_ar="أقلّ من %20 من دخلي الشهري"),
                        FinancialClinicOption(value=3, label_en="Less than 35% of my monthly income", label_ar="أقلّ من %35 من دخلي الشهري"),
                        FinancialClinicOption(value=2, label_en="Less than 50% of my monthly income", label_ar="أقلّ من %50 من دخلي الشهري"),
            FinancialClinicOption(value=1, label_en="More than 50% of my monthly income", label_ar="أكثر من %50 من دخلي الشهري"),
        ]
    ),
    
    # ==================== RETIREMENT PLANNING (Q11-Q13) - 20% ====================
    FinancialClinicQuestion(
        id="fc_q11",
        number=11,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=5,  # 5% of total score
        text_en="Are you actively saving or investing for retirement?",
        text_ar="هل تدخّرون أو تستثمرون بانتظام من أجل التقاعد؟",
        options=[
            FinancialClinicOption(value=5, label_en="Yes, I contribute regularly for a retirement plan and with a specific goal", label_ar="نعم، أنا ادخر بانتظام في خطة للتقاعد وبهدف محدّد"),
            FinancialClinicOption(value=4, label_en="Yes, I save for retirement occasionally, but my contributions vary depending on my monthly expenses", label_ar="نعم، أدّخر للتقاعد أحياناً، لكنّ مساهماتي تختلف بحسب نفقاتي الشهرية."),
            FinancialClinicOption(value=3, label_en="I have started saving or investing for retirement, but I don't have a clear plan or specific goal", label_ar="لقد بدأتُ بالادخار أو الاستثمار للتقاعد، لكن ليس لديّ خطة واضحة أو هدف محدّد."),
            FinancialClinicOption(value=2, label_en="Yes, but I save whenever I can and without a clear plan", label_ar="نعم، لكنّي أدخر كلّما استطعت وبدون خطة واضحة"),
            FinancialClinicOption(value=1, label_en="No, I have not thought about saving for retirement", label_ar="لا، لم أفكّر في مسألة الادّخار من أجل التقاعد."),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q12",
        number=12,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=10,  # 10% of total score
        text_en="How confident do you feel about maintaining a comfortable lifestyle after retirement?",
        text_ar="ما مدى ثقتكم في أنّكم ستُحافظون على أسلوب حياة مريح بعد التقاعد؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I have already secured a retirement income", label_ar="لقد أمّنت بالفعل دخلاً للتقاعد"),
                            FinancialClinicOption(value=4, label_en="I am highly confident of having a stable income after retirement", label_ar="أنا واثق تمامًا من الحصول على دخل ثابت بعد التقاعد."),
                        FinancialClinicOption(value=3, label_en="I am somewhat confident of having a stable income after retirement", label_ar="أنا واثقٌ إلى حدّ ما من الحصول على دخل ثابت بعد التقاعد"),
                        FinancialClinicOption(value=2, label_en="I am not very confident of having a stable income after retirement", label_ar="لست واثقاً تماماً من الحصول على دخل ثابت بعد التقاعد"),
                        FinancialClinicOption(value=1, label_en="I am certain I will not have a stable income after retirement", label_ar="أنا متأكد من أنّه لن يكون لدي دخل ثابت بعد التقاعد"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q13",
        number=13,
        category=FinancialClinicCategory.RETIREMENT_PLANNING,
        weight=5,  # 5% of total score
        text_en="How much of your current income will you be able to cover after your retirement?",
        text_ar="ما النسبة من دخلكم الحالي التي تتوقعون أن تتمكنوا من تغطيتها بعد التقاعد؟",
        options=[
                            FinancialClinicOption(value=5, label_en="My retirement income will be able to provide more than 80% of my current income", label_ar="سيغطي دخلي التقاعدي أكثر من %80 من دخلي الحالي"),
                            FinancialClinicOption(value=4, label_en="My retirement income will be able to provide 50% to 80% of my current income", label_ar="سيغطي دخلي التقاعدي من %50 إلى %80 من دخلي الحالي"),
                        FinancialClinicOption(value=3, label_en="My retirement income will be able to provide 20% to 50% of my current income", label_ar="سيغطي دخلي التقاعدي من %20 إلى %50 من دخلي الحالي"),
                        FinancialClinicOption(value=2, label_en="My retirement income will be able to provide up to 20% of my current income", label_ar="سيغطي دخلي التقاعدي ما يصل إلى %20 من دخلي الحالي"),
                        FinancialClinicOption(value=1, label_en="I am certain I will not have a stable income after retirement", label_ar="أنا متأكد من أنّه لن يكون لدي دخل ثابت بعد التقاعد"),
        ]
    ),
    
    # ==================== PROTECTING YOUR FAMILY (Q14-Q15) - 15% ====================
    FinancialClinicQuestion(
        id="fc_q14",
        number=14,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Do you have adequate life Takaful/Insurance coverage?",
        text_ar="هل لديكم تأمين تكافلي/تأمين على الحياة يوفّر تغطية كافية؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I have sufficient coverage to cover 12 months of my income", label_ar="لديّ تغطية كافية لتعويض دخلي لمدة 12 شهراً"),
                            FinancialClinicOption(value=4, label_en="I have sufficient coverage to cover up to 11 months of my income", label_ar="لديّ تغطية كافية لتعويض دخلي لمدة تصل إلى 11 شهراً"),
                        FinancialClinicOption(value=3, label_en="I have enough coverage to cover up to 5 months of my income", label_ar="لديّ تغطية كافية لتعويض دخلي لمدة تصل إلى 5 أشهر"),
                        FinancialClinicOption(value=2, label_en="I have enough coverage for up to 3 months of my income", label_ar="لديّ تغطية كافية لتعويض دخلي لمدة تصل إلى 3 أشهر"),
                        FinancialClinicOption(value=1, label_en="I do not have any coverage", label_ar="ليس لديّ أيّ تغطية"),
        ]
    ),
    FinancialClinicQuestion(
        id="fc_q15",
        number=15,
        category=FinancialClinicCategory.PROTECTING_FAMILY,
        weight=5,  # 5% of total score
        text_en="Are you actively saving for education savings for your children?",
        text_ar="هل تقومون بالادخار بشكل منتظم لتغطية نفقات تعليم أبنائكم؟",
        options=[
                            FinancialClinicOption(value=5, label_en="I don't have any need to save for my children's education", label_ar="لست بحاجة للادخار من أجل تعليم أبنائي"),
                            FinancialClinicOption(value=4, label_en="Yes, I have sufficient funds for my children's education", label_ar="نعم، لديّ أموال كافية لتعليم أبنائي"),
                        FinancialClinicOption(value=3, label_en="Yes, I am saving towards having a sufficient education fund", label_ar="نعم، أنا أدّخر من أجل ضمان تمويل كافٍ لتعليم أبنائي"),
                        FinancialClinicOption(value=2, label_en="Yes, but I am starting to save for an education fund", label_ar="نعم، لكنّي بدأت بالادخار لصندوق تمويل التعليم"),
                        FinancialClinicOption(value=1, label_en="Yes, but I do not have any education saving for my children", label_ar="نعم، لكن ليس لديّ أيّ مدخرات مخصّصة لتعليم أبنائي"),
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
    """
    Get a specific question by ID.
    
    Args:
        question_id: Question ID (e.g., 'fc_q1', 'fc_q2', etc.)
        
    Returns:
        FinancialClinicQuestion object or None if not found
    """
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
