"""
Unit tests for question definitions module.
Tests question lookup functions, weight calculations, and conditional logic.
"""
import pytest
from app.surveys.question_definitions import (
    QuestionLookup,
    FinancialFactor,
    QuestionDefinition,
    SURVEY_QUESTIONS_V2,
    PILLAR_DEFINITIONS,
    question_lookup,
    get_question_by_id,
    get_questions_by_factor,
    validate_response
)


class TestQuestionDefinitions:
    """Test the question definitions data structure."""
    
    def test_survey_questions_v2_structure(self):
        """Test that SURVEY_QUESTIONS_V2 has the correct structure."""
        assert len(SURVEY_QUESTIONS_V2) == 16, "Should have 16 questions"
        
        # Check that all questions have required fields
        for question in SURVEY_QUESTIONS_V2:
            assert isinstance(question, QuestionDefinition)
            assert question.id.startswith('q')
            assert 1 <= question.question_number <= 16
            assert len(question.text) > 0
            assert question.type == "likert"
            assert len(question.options) == 5  # All should be 5-point Likert
            assert isinstance(question.required, bool)
            assert isinstance(question.factor, FinancialFactor)
            assert question.weight > 0
    
    def test_question_weights_total_100_percent(self):
        """Test that question weights total 95% without conditional questions."""
        total_weight = sum(q.weight for q in SURVEY_QUESTIONS_V2 if not q.conditional)
        assert total_weight == 95, f"Non-conditional questions should total 95%, got {total_weight}%"
    
    def test_question_weights_with_conditional(self):
        """Test that question weights total 100% with conditional Q16."""
        total_weight = sum(q.weight for q in SURVEY_QUESTIONS_V2)
        assert total_weight == 100, f"All questions should total 100%, got {total_weight}%"
    
    def test_conditional_question_q16(self):
        """Test that Q16 is the only conditional question."""
        conditional_questions = [q for q in SURVEY_QUESTIONS_V2 if q.conditional]
        assert len(conditional_questions) == 1, "Should have exactly one conditional question"
        assert conditional_questions[0].id == "q16_children_planning"
        assert conditional_questions[0].required is False
    
    def test_pillar_definitions_structure(self):
        """Test that pillar definitions have correct structure."""
        assert len(PILLAR_DEFINITIONS) == 7, "Should have 7 pillars"
        
        for factor, definition in PILLAR_DEFINITIONS.items():
            assert isinstance(factor, FinancialFactor)
            assert 'name' in definition
            assert 'description' in definition
            assert 'questions' in definition
            assert 'base_weight' in definition
            assert isinstance(definition['questions'], list)
            assert len(definition['questions']) > 0
    
    def test_pillar_question_mapping_consistency(self):
        """Test that pillar definitions match question factors."""
        for factor, definition in PILLAR_DEFINITIONS.items():
            for question_id in definition['questions']:
                question = get_question_by_id(question_id)
                assert question is not None, f"Question {question_id} not found"
                assert question.factor == factor, f"Question {question_id} factor mismatch"


class TestQuestionLookup:
    """Test the QuestionLookup utility class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.lookup = QuestionLookup()
    
    def test_get_question_by_id(self):
        """Test getting question by ID."""
        # Test valid question ID
        question = self.lookup.get_question_by_id("q1_income_stability")
        assert question is not None
        assert question.id == "q1_income_stability"
        assert question.question_number == 1
        assert question.factor == FinancialFactor.INCOME_STREAM
        
        # Test invalid question ID
        question = self.lookup.get_question_by_id("invalid_id")
        assert question is None
    
    def test_get_question_by_number(self):
        """Test getting question by number."""
        # Test valid question number
        question = self.lookup.get_question_by_number(1)
        assert question is not None
        assert question.id == "q1_income_stability"
        assert question.question_number == 1
        
        # Test invalid question number
        question = self.lookup.get_question_by_number(99)
        assert question is None
    
    def test_get_questions_by_factor(self):
        """Test getting questions by financial factor."""
        # Test income stream questions
        income_questions = self.lookup.get_questions_by_factor(FinancialFactor.INCOME_STREAM)
        assert len(income_questions) == 2
        question_ids = [q.id for q in income_questions]
        assert "q1_income_stability" in question_ids
        assert "q2_income_sources" in question_ids
        
        # Test monthly expenses questions
        expense_questions = self.lookup.get_questions_by_factor(FinancialFactor.MONTHLY_EXPENSES)
        assert len(expense_questions) == 4
        
        # Test future planning questions (includes conditional Q16)
        future_questions = self.lookup.get_questions_by_factor(FinancialFactor.FUTURE_PLANNING)
        assert len(future_questions) == 2
        question_ids = [q.id for q in future_questions]
        assert "q15_financial_planning" in question_ids
        assert "q16_children_planning" in question_ids
    
    def test_get_question_weight(self):
        """Test getting question weight."""
        # Test regular question weight
        weight = self.lookup.get_question_weight("q1_income_stability")
        assert weight == 10
        
        # Test conditional question weight
        weight = self.lookup.get_question_weight("q16_children_planning")
        assert weight == 5
        
        # Test invalid question ID
        weight = self.lookup.get_question_weight("invalid_id")
        assert weight == 0
    
    def test_is_question_conditional(self):
        """Test checking if question is conditional."""
        # Test non-conditional question
        assert not self.lookup.is_question_conditional("q1_income_stability")
        
        # Test conditional question
        assert self.lookup.is_question_conditional("q16_children_planning")
        
        # Test invalid question ID
        assert not self.lookup.is_question_conditional("invalid_id")
    
    def test_is_question_required(self):
        """Test checking if question is required."""
        # Test required question
        assert self.lookup.is_question_required("q1_income_stability")
        
        # Test non-required conditional question
        assert not self.lookup.is_question_required("q16_children_planning")
        
        # Test invalid question ID (defaults to True)
        assert self.lookup.is_question_required("invalid_id")
    
    def test_get_all_question_ids(self):
        """Test getting all question IDs."""
        question_ids = self.lookup.get_all_question_ids()
        assert len(question_ids) == 16
        assert "q1_income_stability" in question_ids
        assert "q16_children_planning" in question_ids
    
    def test_get_conditional_questions(self):
        """Test getting conditional questions."""
        conditional_questions = self.lookup.get_conditional_questions()
        assert len(conditional_questions) == 1
        assert conditional_questions[0].id == "q16_children_planning"
    
    def test_get_required_questions(self):
        """Test getting required questions."""
        required_questions = self.lookup.get_required_questions()
        assert len(required_questions) == 15  # All except Q16
        
        # Check that Q16 is not in required questions
        required_ids = [q.id for q in required_questions]
        assert "q16_children_planning" not in required_ids
    
    def test_validate_question_response(self):
        """Test validating question responses."""
        # Test valid Likert scale responses
        assert self.lookup.validate_question_response("q1_income_stability", 1)
        assert self.lookup.validate_question_response("q1_income_stability", 3)
        assert self.lookup.validate_question_response("q1_income_stability", 5)
        assert self.lookup.validate_question_response("q1_income_stability", "3")
        
        # Test invalid Likert scale responses
        assert not self.lookup.validate_question_response("q1_income_stability", 0)
        assert not self.lookup.validate_question_response("q1_income_stability", 6)
        assert not self.lookup.validate_question_response("q1_income_stability", "invalid")
        
        # Test invalid question ID
        assert not self.lookup.validate_question_response("invalid_id", 3)
    
    def test_get_pillar_questions(self):
        """Test getting questions for a pillar."""
        # Test income stream pillar
        income_questions = self.lookup.get_pillar_questions(FinancialFactor.INCOME_STREAM)
        assert income_questions == ["q1_income_stability", "q2_income_sources"]
        
        # Test monthly expenses pillar
        expense_questions = self.lookup.get_pillar_questions(FinancialFactor.MONTHLY_EXPENSES)
        expected = ["q3_living_expenses", "q4_budget_tracking", "q5_spending_control", "q6_expense_review"]
        assert expense_questions == expected
        
        # Test future planning pillar (includes conditional Q16)
        future_questions = self.lookup.get_pillar_questions(FinancialFactor.FUTURE_PLANNING)
        assert future_questions == ["q15_financial_planning", "q16_children_planning"]
    
    def test_get_pillar_base_weight(self):
        """Test getting pillar base weights."""
        assert self.lookup.get_pillar_base_weight(FinancialFactor.INCOME_STREAM) == 20
        assert self.lookup.get_pillar_base_weight(FinancialFactor.MONTHLY_EXPENSES) == 25
        assert self.lookup.get_pillar_base_weight(FinancialFactor.SAVINGS_HABIT) == 15
        assert self.lookup.get_pillar_base_weight(FinancialFactor.DEBT_MANAGEMENT) == 15
        assert self.lookup.get_pillar_base_weight(FinancialFactor.RETIREMENT_PLANNING) == 10
        assert self.lookup.get_pillar_base_weight(FinancialFactor.PROTECTION) == 5
        assert self.lookup.get_pillar_base_weight(FinancialFactor.FUTURE_PLANNING) == 10
    
    def test_calculate_total_weight(self):
        """Test calculating total weight."""
        # Without conditional questions
        total_without_conditional = self.lookup.calculate_total_weight(include_conditional=False)
        assert total_without_conditional == 95
        
        # With conditional questions
        total_with_conditional = self.lookup.calculate_total_weight(include_conditional=True)
        assert total_with_conditional == 100


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_get_question_by_id_function(self):
        """Test the convenience function for getting question by ID."""
        question = get_question_by_id("q1_income_stability")
        assert question is not None
        assert question.id == "q1_income_stability"
        
        question = get_question_by_id("invalid_id")
        assert question is None
    
    def test_get_questions_by_factor_function(self):
        """Test the convenience function for getting questions by factor."""
        questions = get_questions_by_factor(FinancialFactor.INCOME_STREAM)
        assert len(questions) == 2
        
        question_ids = [q.id for q in questions]
        assert "q1_income_stability" in question_ids
        assert "q2_income_sources" in question_ids
    
    def test_validate_response_function(self):
        """Test the convenience function for validating responses."""
        assert validate_response("q1_income_stability", 3)
        assert not validate_response("q1_income_stability", 0)
        assert not validate_response("invalid_id", 3)


class TestQuestionWeightDistribution:
    """Test that question weights match the expected distribution."""
    
    def test_income_stream_weights(self):
        """Test income stream question weights (20% total)."""
        questions = get_questions_by_factor(FinancialFactor.INCOME_STREAM)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 20, f"Income stream should be 20%, got {total_weight}%"
    
    def test_monthly_expenses_weights(self):
        """Test monthly expenses question weights (25% total)."""
        questions = get_questions_by_factor(FinancialFactor.MONTHLY_EXPENSES)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 25, f"Monthly expenses should be 25%, got {total_weight}%"
    
    def test_savings_habit_weights(self):
        """Test savings habit question weights (15% total)."""
        questions = get_questions_by_factor(FinancialFactor.SAVINGS_HABIT)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 15, f"Savings habit should be 15%, got {total_weight}%"
    
    def test_debt_management_weights(self):
        """Test debt management question weights (15% total)."""
        questions = get_questions_by_factor(FinancialFactor.DEBT_MANAGEMENT)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 15, f"Debt management should be 15%, got {total_weight}%"
    
    def test_retirement_planning_weights(self):
        """Test retirement planning question weights (10% total)."""
        questions = get_questions_by_factor(FinancialFactor.RETIREMENT_PLANNING)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 10, f"Retirement planning should be 10%, got {total_weight}%"
    
    def test_protection_weights(self):
        """Test protection question weights (5% total)."""
        questions = get_questions_by_factor(FinancialFactor.PROTECTION)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 5, f"Protection should be 5%, got {total_weight}%"
    
    def test_future_planning_weights(self):
        """Test future planning question weights (10% total: 5% + 5%)."""
        questions = get_questions_by_factor(FinancialFactor.FUTURE_PLANNING)
        total_weight = sum(q.weight for q in questions)
        assert total_weight == 10, f"Future planning should be 10%, got {total_weight}%"
        
        # Check individual question weights
        q15 = get_question_by_id("q15_financial_planning")
        q16 = get_question_by_id("q16_children_planning")
        assert q15.weight == 5
        assert q16.weight == 5


class TestQuestionContent:
    """Test specific question content matches frontend exactly."""
    
    def test_q1_content(self):
        """Test Q1 content matches frontend."""
        q1 = get_question_by_id("q1_income_stability")
        assert q1.question_number == 1
        assert q1.text == "My income is stable and predictable each month."
        assert q1.factor == FinancialFactor.INCOME_STREAM
        assert q1.weight == 10
        assert q1.required is True
        assert q1.conditional is False
    
    def test_q16_content(self):
        """Test Q16 content matches frontend (conditional question)."""
        q16 = get_question_by_id("q16_children_planning")
        assert q16.question_number == 16
        assert "children future" in q16.text
        assert q16.factor == FinancialFactor.FUTURE_PLANNING
        assert q16.weight == 5
        assert q16.required is False
        assert q16.conditional is True
    
    def test_likert_options_structure(self):
        """Test that all questions have proper 5-point Likert options."""
        for question in SURVEY_QUESTIONS_V2:
            assert len(question.options) == 5
            values = [opt.value for opt in question.options]
            assert values == [5, 4, 3, 2, 1], f"Question {question.id} has incorrect option values"
            
            # Check that all options have labels
            for option in question.options:
                assert len(option.label) > 0, f"Question {question.id} has empty option label"