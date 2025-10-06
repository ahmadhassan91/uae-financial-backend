"""
End-to-end test for conditional Q16 scoring functionality.

This test verifies that the conditional Q16 logic works correctly
with the updated survey routes and profile data.
"""
import pytest
from app.surveys.scoring import SurveyScorer


class TestQ16EndToEnd:
    """End-to-end tests for Q16 conditional logic."""
    
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
            'q16_children_planning': 4
        }
    
    def test_scoring_with_children_profile(self):
        """Test scoring with a profile that has children."""
        # Profile data as it would come from CustomerProfile model
        profile_data = {'children': 'Yes'}
        
        result = self.scorer.calculate_scores_v2(self.base_responses, profile_data)
        
        # Verify Q16 is included
        assert result['max_possible_score'] == 80
        assert result['total_weight'] == 100
        
        # Verify future planning pillar includes Q16
        future_planning_pillar = next(
            (p for p in result['pillar_scores'] if p['factor'] == 'future_planning'), 
            None
        )
        assert future_planning_pillar is not None
        assert future_planning_pillar['weight'] == 10  # 5 + 5 (Q15 + Q16)
    
    def test_scoring_without_children_profile(self):
        """Test scoring with a profile that doesn't have children."""
        # Profile data as it would come from CustomerProfile model
        profile_data = {'children': 'No'}
        
        result = self.scorer.calculate_scores_v2(self.base_responses, profile_data)
        
        # Verify Q16 is excluded
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
        
        # Verify future planning pillar excludes Q16
        future_planning_pillar = next(
            (p for p in result['pillar_scores'] if p['factor'] == 'future_planning'), 
            None
        )
        assert future_planning_pillar is not None
        assert future_planning_pillar['weight'] == 5  # Only Q15
    
    def test_scoring_with_none_profile(self):
        """Test scoring with None profile (guest user scenario)."""
        result = self.scorer.calculate_scores_v2(self.base_responses, None)
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_scoring_with_empty_profile(self):
        """Test scoring with empty profile dict."""
        result = self.scorer.calculate_scores_v2(self.base_responses, {})
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_score_difference_with_and_without_children(self):
        """Test that scores are different when Q16 is included vs excluded."""
        # Score with children (Q16 included)
        profile_with_children = {'children': 'Yes'}
        result_with_children = self.scorer.calculate_scores_v2(
            self.base_responses, 
            profile_with_children
        )
        
        # Score without children (Q16 excluded)
        profile_without_children = {'children': 'No'}
        result_without_children = self.scorer.calculate_scores_v2(
            self.base_responses, 
            profile_without_children
        )
        
        # Scores should be different due to different max scores and weights
        assert result_with_children['total_score'] != result_without_children['total_score']
        assert result_with_children['max_possible_score'] == 80
        assert result_without_children['max_possible_score'] == 75
    
    def test_q16_response_value_affects_score_when_included(self):
        """Test that Q16 response value affects the score when user has children."""
        profile_with_children = {'children': 'Yes'}
        
        # Test with Q16 = 1 (lowest)
        responses_low = self.base_responses.copy()
        responses_low['q16_children_planning'] = 1
        result_low = self.scorer.calculate_scores_v2(responses_low, profile_with_children)
        
        # Test with Q16 = 5 (highest)
        responses_high = self.base_responses.copy()
        responses_high['q16_children_planning'] = 5
        result_high = self.scorer.calculate_scores_v2(responses_high, profile_with_children)
        
        # Higher Q16 should result in higher total score
        assert result_high['total_score'] > result_low['total_score']
        
        # Both should have same max score and total weight
        assert result_low['max_possible_score'] == 80
        assert result_high['max_possible_score'] == 80
        assert result_low['total_weight'] == 100
        assert result_high['total_weight'] == 100
    
    def test_q16_response_ignored_when_no_children(self):
        """Test that Q16 response is ignored when user doesn't have children."""
        profile_without_children = {'children': 'No'}
        
        # Test with different Q16 values
        responses_q16_1 = self.base_responses.copy()
        responses_q16_1['q16_children_planning'] = 1
        
        responses_q16_5 = self.base_responses.copy()
        responses_q16_5['q16_children_planning'] = 5
        
        result_1 = self.scorer.calculate_scores_v2(responses_q16_1, profile_without_children)
        result_5 = self.scorer.calculate_scores_v2(responses_q16_5, profile_without_children)
        
        # Results should be identical since Q16 is ignored
        assert result_1['total_score'] == result_5['total_score']
        assert result_1['max_possible_score'] == result_5['max_possible_score']
        assert result_1['total_weight'] == result_5['total_weight']
    
    def test_legacy_calculate_scores_still_works(self):
        """Test that the legacy calculate_scores method still works for backward compatibility."""
        result = self.scorer.calculate_scores(self.base_responses)
        
        # Should return the legacy format
        assert 'overall_score' in result
        assert 'budgeting_score' in result
        assert 'savings_score' in result
        assert 'debt_management_score' in result
        assert 'financial_planning_score' in result
        assert 'investment_knowledge_score' in result
        
        # All scores should be numeric
        for score in result.values():
            assert isinstance(score, (int, float))
            assert score >= 0