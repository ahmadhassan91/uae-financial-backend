"""
Test conditional Q16 scoring logic to ensure proper implementation.

This test suite verifies that:
1. Q16 is included in scoring when user has children
2. Q16 is excluded from scoring when user doesn't have children  
3. Max score calculation adjusts correctly (75 vs 80)
4. Pillar weights are calculated correctly with/without Q16
5. Total score calculation matches frontend implementation
"""
import pytest
from app.surveys.scoring import SurveyScorer
from app.surveys.question_definitions import question_lookup


class TestConditionalQ16Scoring:
    """Test conditional Q16 scoring logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = SurveyScorer()
        
        # Sample survey responses (all questions answered with value 4)
        self.base_responses = {
            'q1_income_stability': 4,
            'q2_income_sources': 4,
            'q3_living_expenses': 4,
            'q4_budget_tracking': 4,
            'q5_spending_control': 4,
            'q6_expense_review': 4,
            'q7_savings_rate': 4,
            'q8_emergency_fund': 4,
            'q9_savings_optimization': 4,
            'q10_payment_history': 4,
            'q11_debt_ratio': 4,
            'q12_credit_score': 4,
            'q13_retirement_planning': 4,
            'q14_insurance_coverage': 4,
            'q15_financial_planning': 4,
            'q16_children_planning': 4  # This should be conditional
        }
        
        # Profile with children
        self.profile_with_children = {'children': 'Yes'}
        
        # Profile without children
        self.profile_without_children = {'children': 'No'}
        
        # Profile with no children field (should default to No)
        self.profile_no_children_field = {}
    
    def test_q16_included_when_has_children(self):
        """Test that Q16 is included in scoring when user has children."""
        result = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_with_children
        )
        
        # Check that future_planning pillar includes Q16
        future_planning_pillar = next(
            (p for p in result['pillar_scores'] if p['factor'] == 'future_planning'), 
            None
        )
        
        assert future_planning_pillar is not None
        # With Q16, future planning should have weight of 10 (5 + 5)
        assert future_planning_pillar['weight'] == 10
        
        # Max score should be 80 when Q16 is included
        assert result['max_possible_score'] == 80
        
        # Total weight should be 100 (all questions included)
        assert result['total_weight'] == 100
    
    def test_q16_excluded_when_no_children(self):
        """Test that Q16 is excluded from scoring when user doesn't have children."""
        result = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_without_children
        )
        
        # Check that future_planning pillar excludes Q16
        future_planning_pillar = next(
            (p for p in result['pillar_scores'] if p['factor'] == 'future_planning'), 
            None
        )
        
        assert future_planning_pillar is not None
        # Without Q16, future planning should have weight of 5 (only q15)
        assert future_planning_pillar['weight'] == 5
        
        # Max score should be 75 when Q16 is excluded
        assert result['max_possible_score'] == 75
        
        # Total weight should be 95 (Q16's 5% excluded)
        assert result['total_weight'] == 95
    
    def test_q16_excluded_when_no_children_field(self):
        """Test that Q16 is excluded when profile has no children field."""
        result = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_no_children_field
        )
        
        # Should behave same as profile_without_children
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_pillar_weight_calculation_with_children(self):
        """Test pillar weight calculation when user has children."""
        # Future planning pillar should have weight 10 with children
        weight = self.scorer.get_pillar_weight_calculation('future_planning', has_children=True)
        assert weight == 10
        
        # Total weight should be 100 with children
        total_weight = self.scorer.get_total_possible_weight(has_children=True)
        assert total_weight == 100
    
    def test_pillar_weight_calculation_without_children(self):
        """Test pillar weight calculation when user doesn't have children."""
        # Future planning pillar should have weight 5 without children
        weight = self.scorer.get_pillar_weight_calculation('future_planning', has_children=False)
        assert weight == 5
        
        # Total weight should be 95 without children
        total_weight = self.scorer.get_total_possible_weight(has_children=False)
        assert total_weight == 95
    
    def test_score_calculation_consistency_with_children(self):
        """Test that score calculation is consistent when including Q16."""
        result = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_with_children
        )
        
        # With all responses = 4, weighted average should be 4.0
        expected_weighted_sum = 4.0 * (100 / 100)  # 100% weight, average score 4
        assert abs(result['weighted_sum'] - expected_weighted_sum) < 0.01
        
        # Total score calculation: base(15) + ((avg-1)/4) * range
        # Range = 80-15 = 65, avg = 4, so: 15 + (3/4) * 65 = 15 + 48.75 = 63.75 ≈ 64
        expected_total = 15 + ((4.0 - 1) / 4) * (80 - 15)
        assert abs(result['total_score'] - round(expected_total)) <= 1
    
    def test_score_calculation_consistency_without_children(self):
        """Test that score calculation is consistent when excluding Q16."""
        result = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_without_children
        )
        
        # With all responses = 4, weighted average should be 4.0
        expected_weighted_sum = 4.0 * (95 / 100)  # 95% weight, average score 4
        assert abs(result['weighted_sum'] - expected_weighted_sum) < 0.01
        
        # Total score calculation: base(15) + ((avg-1)/4) * range
        # Range = 75-15 = 60, avg = 4, so: 15 + (3/4) * 60 = 15 + 45 = 60
        expected_total = 15 + ((4.0 - 1) / 4) * (75 - 15)
        assert abs(result['total_score'] - round(expected_total)) <= 1
    
    def test_q16_response_ignored_when_no_children(self):
        """Test that Q16 response is ignored when user doesn't have children."""
        # Create responses without Q16
        responses_without_q16 = {k: v for k, v in self.base_responses.items() if k != 'q16_children_planning'}
        
        # Calculate scores without Q16 response
        result_without_q16 = self.scorer.calculate_scores_v2(
            responses_without_q16, 
            self.profile_without_children
        )
        
        # Calculate scores with Q16 response (should be ignored)
        result_with_q16 = self.scorer.calculate_scores_v2(
            self.base_responses, 
            self.profile_without_children
        )
        
        # Results should be identical since Q16 is ignored
        assert result_without_q16['total_score'] == result_with_q16['total_score']
        assert result_without_q16['max_possible_score'] == result_with_q16['max_possible_score']
        assert result_without_q16['total_weight'] == result_with_q16['total_weight']
    
    def test_different_q16_values_affect_score_with_children(self):
        """Test that different Q16 values affect the score when user has children."""
        # Test with Q16 = 1 (lowest score)
        responses_q16_low = self.base_responses.copy()
        responses_q16_low['q16_children_planning'] = 1
        
        result_low = self.scorer.calculate_scores_v2(
            responses_q16_low, 
            self.profile_with_children
        )
        
        # Test with Q16 = 5 (highest score)
        responses_q16_high = self.base_responses.copy()
        responses_q16_high['q16_children_planning'] = 5
        
        result_high = self.scorer.calculate_scores_v2(
            responses_q16_high, 
            self.profile_with_children
        )
        
        # Higher Q16 score should result in higher total score
        assert result_high['total_score'] > result_low['total_score']
        
        # Both should have same max score (80) and total weight (100)
        assert result_low['max_possible_score'] == 80
        assert result_high['max_possible_score'] == 80
        assert result_low['total_weight'] == 100
        assert result_high['total_weight'] == 100
    
    def test_edge_case_empty_profile(self):
        """Test edge case with empty profile."""
        result = self.scorer.calculate_scores_v2(self.base_responses, {})
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_edge_case_none_profile(self):
        """Test edge case with None profile."""
        result = self.scorer.calculate_scores_v2(self.base_responses, None)
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_question_lookup_conditional_flag(self):
        """Test that Q16 is properly marked as conditional in question definitions."""
        q16 = question_lookup.get_question_by_id('q16_children_planning')
        
        assert q16 is not None
        assert q16.conditional is True
        assert q16.required is False
        assert q16.weight == 5
        
        # Other questions should not be conditional
        q15 = question_lookup.get_question_by_id('q15_financial_planning')
        assert q15.conditional is False
        assert q15.required is True