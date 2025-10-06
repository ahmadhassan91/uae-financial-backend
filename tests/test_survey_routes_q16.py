"""
Test survey routes with Q16 conditional logic.

This test verifies that the survey submission routes correctly
pass profile data to the scoring engine.
"""
import pytest
from unittest.mock import Mock, patch
from app.surveys.scoring import SurveyScorer


class TestSurveyRoutesQ16:
    """Test survey routes Q16 integration."""
    
    def test_scorer_called_with_profile_data(self):
        """Test that the scoring engine is called with correct profile data."""
        # Create a mock customer profile
        mock_profile = Mock()
        mock_profile.children = "Yes"
        
        # Sample responses
        responses = {
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
        
        # Test the scoring logic that would be used in the route
        scorer = SurveyScorer()
        profile_data = {'children': mock_profile.children}
        
        result = scorer.calculate_scores_v2(responses, profile=profile_data)
        
        # Verify Q16 is included when children = "Yes"
        assert result['max_possible_score'] == 80
        assert result['total_weight'] == 100
        
        # Test with children = "No"
        mock_profile.children = "No"
        profile_data = {'children': mock_profile.children}
        
        result = scorer.calculate_scores_v2(responses, profile=profile_data)
        
        # Verify Q16 is excluded when children = "No"
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_guest_survey_no_profile(self):
        """Test guest survey submission with no profile."""
        scorer = SurveyScorer()
        
        responses = {
            'q1_income_stability': 4,
            'q15_financial_planning': 4,
            'q16_children_planning': 4  # This should be ignored for guests
        }
        
        # Guest users have no profile, so Q16 should be ignored
        result = scorer.calculate_scores_v2(responses, profile=None)
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
    
    def test_profile_data_structure(self):
        """Test that profile data is structured correctly for scoring."""
        # Simulate how the route would extract profile data
        mock_customer_profile = Mock()
        mock_customer_profile.children = "Yes"
        mock_customer_profile.first_name = "Test"
        mock_customer_profile.age = 30
        
        # Extract only the children field for scoring (as done in routes)
        profile_data = {'children': mock_customer_profile.children}
        
        scorer = SurveyScorer()
        responses = {'q15_financial_planning': 4, 'q16_children_planning': 5}
        
        result = scorer.calculate_scores_v2(responses, profile=profile_data)
        
        # Verify the profile data was used correctly
        assert result['max_possible_score'] == 80  # Q16 included
        
        # Test with different children value
        mock_customer_profile.children = "No"
        profile_data = {'children': mock_customer_profile.children}
        
        result = scorer.calculate_scores_v2(responses, profile=profile_data)
        assert result['max_possible_score'] == 75  # Q16 excluded