"""
Centralized question definitions module that matches frontend SURVEY_QUESTIONS_V2.
This module provides the authoritative source for question metadata, weights, and conditional logic.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class FinancialFactor(str, Enum):
    """Financial factor categories matching frontend types."""
    INCOME_STREAM = "income_stream"
    MONTHLY_EXPENSES = "monthly_expenses"
    SAVINGS_HABIT = "savings_habit"
    DEBT_MANAGEMENT = "debt_management"
    RETIREMENT_PLANNING = "retirement_planning"
    PROTECTION = "protection"
    FUTURE_PLANNING = "future_planning"


@dataclass
class LikertOption:
    """Likert scale option definition."""
    value: int
    label: str


@dataclass
class QuestionDefinition:
    """Question definition matching frontend Question interface."""
    id: str
    question_number: int
    text: str
    type: str
    options: List[LikertOption]
    required: bool
    factor: FinancialFactor
    weight: int  # percentage (e.g., 10 for 10%)
    conditional: bool = False


# Survey questions matching frontend SURVEY_QUESTIONS_V2 exactly
SURVEY_QUESTIONS_V2: List[QuestionDefinition] = [
    QuestionDefinition(
        id="q1_income_stability",
        question_number=1,
        text="My income is stable and predictable each month.",
        type="likert",
        options=[
            LikertOption(value=5, label="Strongly Agree"),
            LikertOption(value=4, label="Agree"),
            LikertOption(value=3, label="Neutral"),
            LikertOption(value=2, label="Disagree"),
            LikertOption(value=1, label="Strongly Disagree")
        ],
        required=True,
        factor=FinancialFactor.INCOME_STREAM,
        weight=10
    ),
    QuestionDefinition(
        id="q2_income_sources",
        question_number=2,
        text="I have more than one source of income (e.g., side business, investments).",
        type="likert",
        options=[
            LikertOption(value=5, label="Multiple consistent income streams"),
            LikertOption(value=4, label="Multiple inconsistent income streams"),
            LikertOption(value=3, label="I have a consistent side income"),
            LikertOption(value=2, label="A non consistent side income"),
            LikertOption(value=1, label="My Salary")
        ],
        required=True,
        factor=FinancialFactor.INCOME_STREAM,
        weight=10
    ),
    QuestionDefinition(
        id="q3_living_expenses",
        question_number=3,
        text="I can cover my essential living expenses without financial strain.",
        type="likert",
        options=[
            LikertOption(value=5, label="Strongly Agree"),
            LikertOption(value=4, label="Agree"),
            LikertOption(value=3, label="Neutral"),
            LikertOption(value=2, label="Disagree"),
            LikertOption(value=1, label="Strongly Disagree")
        ],
        required=True,
        factor=FinancialFactor.MONTHLY_EXPENSES,
        weight=10
    ),
    QuestionDefinition(
        id="q4_budget_tracking",
        question_number=4,
        text="I follow a monthly budget and track my expenses.",
        type="likert",
        options=[
            LikertOption(value=5, label="Consistently every month"),
            LikertOption(value=4, label="Frequently but not consistently"),
            LikertOption(value=3, label="Occasionally"),
            LikertOption(value=2, label="Adhoc"),
            LikertOption(value=1, label="No Tracking")
        ],
        required=True,
        factor=FinancialFactor.MONTHLY_EXPENSES,
        weight=5
    ),
    QuestionDefinition(
        id="q5_spending_control",
        question_number=5,
        text="I spend less than I earn every month.",
        type="likert",
        options=[
            LikertOption(value=5, label="Consistently every month"),
            LikertOption(value=4, label="Frequently but not consistently"),
            LikertOption(value=3, label="Occasionally"),
            LikertOption(value=2, label="Adhoc"),
            LikertOption(value=1, label="Greater or all of my earnings")
        ],
        required=True,
        factor=FinancialFactor.MONTHLY_EXPENSES,
        weight=5
    ),
    QuestionDefinition(
        id="q6_expense_review",
        question_number=6,
        text="I regularly review and reduce unnecessary expenses.",
        type="likert",
        options=[
            LikertOption(value=5, label="Consistently every month"),
            LikertOption(value=4, label="Frequently but not consistently"),
            LikertOption(value=3, label="Occasionally"),
            LikertOption(value=2, label="Adhoc"),
            LikertOption(value=1, label="No Tracking")
        ],
        required=True,
        factor=FinancialFactor.MONTHLY_EXPENSES,
        weight=5
    ),
    QuestionDefinition(
        id="q7_savings_rate",
        question_number=7,
        text="I save from my income every month.",
        type="likert",
        options=[
            LikertOption(value=5, label="20% or more"),
            LikertOption(value=4, label="Less than 20%"),
            LikertOption(value=3, label="Less than 10%"),
            LikertOption(value=2, label="5% or less"),
            LikertOption(value=1, label="0%")
        ],
        required=True,
        factor=FinancialFactor.SAVINGS_HABIT,
        weight=5
    ),
    QuestionDefinition(
        id="q8_emergency_fund",
        question_number=8,
        text="I have an emergency fund to cater for my expenses.",
        type="likert",
        options=[
            LikertOption(value=5, label="6+ months"),
            LikertOption(value=4, label="3 - 6 months"),
            LikertOption(value=3, label="2 months"),
            LikertOption(value=2, label="1 month"),
            LikertOption(value=1, label="Nil")
        ],
        required=True,
        factor=FinancialFactor.SAVINGS_HABIT,
        weight=5
    ),
    QuestionDefinition(
        id="q9_savings_optimization",
        question_number=9,
        text="I keep my savings in safe, return generating accounts or investments.",
        type="likert",
        options=[
            LikertOption(value=5, label="Safe | Seek for return optimization consistently"),
            LikertOption(value=4, label="Safe | Seek for return optimization most of the times"),
            LikertOption(value=3, label="Savings Account with minimal returns"),
            LikertOption(value=2, label="Current Account"),
            LikertOption(value=1, label="Cash")
        ],
        required=True,
        factor=FinancialFactor.SAVINGS_HABIT,
        weight=5
    ),
    QuestionDefinition(
        id="q10_payment_history",
        question_number=10,
        text="I pay all my bills and loan installments on time.",
        type="likert",
        options=[
            LikertOption(value=5, label="Consistently every month"),
            LikertOption(value=4, label="Frequently but not consistently"),
            LikertOption(value=3, label="Occasionally"),
            LikertOption(value=2, label="Adhoc"),
            LikertOption(value=1, label="Missed Payments most of the times")
        ],
        required=True,
        factor=FinancialFactor.DEBT_MANAGEMENT,
        weight=5
    ),
    QuestionDefinition(
        id="q11_debt_ratio",
        question_number=11,
        text="My debt repayments are less than 30% of my monthly income.",
        type="likert",
        options=[
            LikertOption(value=5, label="No Debt"),
            LikertOption(value=4, label="20% or less of monthly income"),
            LikertOption(value=3, label="Less than 30% of monthly income"),
            LikertOption(value=2, label="30% or more of monthly income"),
            LikertOption(value=1, label="50% or more of monthly income")
        ],
        required=True,
        factor=FinancialFactor.DEBT_MANAGEMENT,
        weight=5
    ),
    QuestionDefinition(
        id="q12_credit_score",
        question_number=12,
        text="I understand my credit score and actively maintain or improve it.",
        type="likert",
        options=[
            LikertOption(value=5, label="100% and monitor it consistently"),
            LikertOption(value=4, label="100% and monitor it frequently"),
            LikertOption(value=3, label="somewhat understand and frequent monitoring"),
            LikertOption(value=2, label="somewhat understand and maintain on an adhoc basis"),
            LikertOption(value=1, label="No Understanding and not maintained")
        ],
        required=True,
        factor=FinancialFactor.DEBT_MANAGEMENT,
        weight=5
    ),
    QuestionDefinition(
        id="q13_retirement_planning",
        question_number=13,
        text="I have a retirement savings plan or pension fund in place to secure a stable income at retirement.",
        type="likert",
        options=[
            LikertOption(value=5, label="Yes - I have already secured a stable income"),
            LikertOption(value=4, label="Yes - I am highly confident of having a stable income"),
            LikertOption(value=3, label="Yes - I am somewhat confident of having a stable income"),
            LikertOption(value=2, label="No: Planning to have one shortly | adhoc Savings"),
            LikertOption(value=1, label="No: not for the time being")
        ],
        required=True,
        factor=FinancialFactor.RETIREMENT_PLANNING,
        weight=10
    ),
    QuestionDefinition(
        id="q14_insurance_coverage",
        question_number=14,
        text="I have adequate takaful cover (insurance) - (health, life, motor, property).",
        type="likert",
        options=[
            LikertOption(value=5, label="100% adequate cover in place for the required protection"),
            LikertOption(value=4, label="80% cover in place for the required protection"),
            LikertOption(value=3, label="50% cover in place for the required protection"),
            LikertOption(value=2, label="25% cover in place for the required protection"),
            LikertOption(value=1, label="No Coverage")
        ],
        required=True,
        factor=FinancialFactor.PROTECTION,
        weight=5
    ),
    QuestionDefinition(
        id="q15_financial_planning",
        question_number=15,
        text="I have a written financial plan with goals for the next 3–5 years catering.",
        type="likert",
        options=[
            LikertOption(value=5, label="Concise Financial plan in place and consistently reviewed"),
            LikertOption(value=4, label="Broad Financial plan in place and frequently reviewed"),
            LikertOption(value=3, label="High level objectives set and occasionally reviewed"),
            LikertOption(value=2, label="Adhoc Plan | reviews"),
            LikertOption(value=1, label="No Financial Plan in place")
        ],
        required=True,
        factor=FinancialFactor.FUTURE_PLANNING,
        weight=5
    ),
    QuestionDefinition(
        id="q16_children_planning",
        question_number=16,
        text="I have adequately planned my children future for his school | University | Career Start Up.",
        type="likert",
        options=[
            LikertOption(value=5, label="100% adequate savings in place for all 3 Aspects"),
            LikertOption(value=4, label="80% savings in place for all 3 Aspects"),
            LikertOption(value=3, label="50% savings in place for all 3 Aspects"),
            LikertOption(value=2, label="Adhoc plan in place for all 3 Aspects"),
            LikertOption(value=1, label="No Plan in place")
        ],
        required=False,  # Conditional based on having children
        factor=FinancialFactor.FUTURE_PLANNING,
        weight=5,
        conditional=True
    )
]

# Pillar definitions matching frontend PILLAR_DEFINITIONS exactly
PILLAR_DEFINITIONS = {
    FinancialFactor.INCOME_STREAM: {
        'name': 'Income Stream',
        'description': 'Stability and diversity of income sources',
        'questions': ['q1_income_stability', 'q2_income_sources'],
        'base_weight': 20
    },
    FinancialFactor.MONTHLY_EXPENSES: {
        'name': 'Monthly Expenses Management',
        'description': 'Budgeting and expense control',
        'questions': ['q3_living_expenses', 'q4_budget_tracking', 'q5_spending_control', 'q6_expense_review'],
        'base_weight': 25
    },
    FinancialFactor.SAVINGS_HABIT: {
        'name': 'Savings Habit',
        'description': 'Saving behavior and emergency preparedness',
        'questions': ['q7_savings_rate', 'q8_emergency_fund', 'q9_savings_optimization'],
        'base_weight': 15
    },
    FinancialFactor.DEBT_MANAGEMENT: {
        'name': 'Debt Management',
        'description': 'Debt control and credit health',
        'questions': ['q10_payment_history', 'q11_debt_ratio', 'q12_credit_score'],
        'base_weight': 15
    },
    FinancialFactor.RETIREMENT_PLANNING: {
        'name': 'Retirement Planning',
        'description': 'Long-term financial security',
        'questions': ['q13_retirement_planning'],
        'base_weight': 10
    },
    FinancialFactor.PROTECTION: {
        'name': 'Protecting Your Assets | Loved Ones',
        'description': 'Insurance and risk management',
        'questions': ['q14_insurance_coverage'],
        'base_weight': 5
    },
    FinancialFactor.FUTURE_PLANNING: {
        'name': 'Planning for Your Future | Siblings',
        'description': 'Financial planning and family preparation',
        'questions': ['q15_financial_planning', 'q16_children_planning'],
        'base_weight': 10  # 10 if Q16 applies (5 + 5)
    }
}


class QuestionLookup:
    """Utility class for question lookup and metadata retrieval."""
    
    def __init__(self):
        """Initialize the question lookup with indexed data."""
        self._questions_by_id = {q.id: q for q in SURVEY_QUESTIONS_V2}
        self._questions_by_number = {q.question_number: q for q in SURVEY_QUESTIONS_V2}
        self._questions_by_factor = {}
        
        # Group questions by factor
        for question in SURVEY_QUESTIONS_V2:
            if question.factor not in self._questions_by_factor:
                self._questions_by_factor[question.factor] = []
            self._questions_by_factor[question.factor].append(question)
    
    def get_question_by_id(self, question_id: str) -> Optional[QuestionDefinition]:
        """Get question definition by ID."""
        return self._questions_by_id.get(question_id)
    
    def get_question_by_number(self, question_number: int) -> Optional[QuestionDefinition]:
        """Get question definition by question number."""
        return self._questions_by_number.get(question_number)
    
    def get_questions_by_factor(self, factor: FinancialFactor) -> List[QuestionDefinition]:
        """Get all questions for a specific financial factor."""
        return self._questions_by_factor.get(factor, [])
    
    def get_question_weight(self, question_id: str) -> int:
        """Get the weight percentage for a specific question."""
        question = self.get_question_by_id(question_id)
        return question.weight if question else 0
    
    def is_question_conditional(self, question_id: str) -> bool:
        """Check if a question is conditional (like Q16)."""
        question = self.get_question_by_id(question_id)
        return question.conditional if question else False
    
    def is_question_required(self, question_id: str) -> bool:
        """Check if a question is required."""
        question = self.get_question_by_id(question_id)
        return question.required if question else True
    
    def get_all_question_ids(self) -> List[str]:
        """Get all question IDs."""
        return list(self._questions_by_id.keys())
    
    def get_conditional_questions(self) -> List[QuestionDefinition]:
        """Get all conditional questions."""
        return [q for q in SURVEY_QUESTIONS_V2 if q.conditional]
    
    def get_required_questions(self) -> List[QuestionDefinition]:
        """Get all required questions."""
        return [q for q in SURVEY_QUESTIONS_V2 if q.required]
    
    def validate_question_response(self, question_id: str, response_value: Any) -> bool:
        """Validate if a response value is valid for a question."""
        question = self.get_question_by_id(question_id)
        if not question:
            return False
        
        if question.type == "likert":
            try:
                value = int(response_value)
                return 1 <= value <= 5
            except (ValueError, TypeError):
                return False
        
        return True
    
    def get_pillar_questions(self, pillar: FinancialFactor) -> List[str]:
        """Get question IDs for a specific pillar."""
        return PILLAR_DEFINITIONS.get(pillar, {}).get('questions', [])
    
    def get_pillar_base_weight(self, pillar: FinancialFactor) -> int:
        """Get the base weight percentage for a pillar."""
        return PILLAR_DEFINITIONS.get(pillar, {}).get('base_weight', 0)
    
    def calculate_total_weight(self, include_conditional: bool = False) -> int:
        """Calculate total weight of all questions."""
        total = 0
        for question in SURVEY_QUESTIONS_V2:
            if not question.conditional or include_conditional:
                total += question.weight
        return total


# Global instance for easy access
question_lookup = QuestionLookup()


def get_question_by_id(question_id: str) -> Optional[QuestionDefinition]:
    """Convenience function to get question by ID."""
    return question_lookup.get_question_by_id(question_id)


def get_questions_by_factor(factor: FinancialFactor) -> List[QuestionDefinition]:
    """Convenience function to get questions by factor."""
    return question_lookup.get_questions_by_factor(factor)


def validate_response(question_id: str, response_value: Any) -> bool:
    """Convenience function to validate a response."""
    return question_lookup.validate_question_response(question_id, response_value)