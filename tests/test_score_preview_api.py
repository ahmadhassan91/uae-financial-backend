"""
Test the score preview API endpoint.

This test suite verifies that the new score preview endpoint works correctly
and returns consistent results with the scoring engine.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.surveys.scoring import SurveyScorer


class TestScorePreviewAPI:
    """Test the score preview API endpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
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
    
    def test_score_preview_with_children(self):
        """Test score preview API with children profile."""
        request_data = {
            'responses': self.base_responses,
            'profile': {'children': 'Yes'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert 'total_score' in result
        assert 'max_possible_score' in result
        assert 'pillar_scores' in result
        assert 'weighted_sum' in result
        assert 'total_weight' in result
        assert 'average_score' in result
        
        # Verify values match backend calculation
        backend_result = self.scorer.calculate_scores_v2(self.base_responses, {'children': 'Yes'})
        
        assert result['total_score'] == backend_result['total_score']
        assert result['max_possible_score'] == backend_result['max_possible_score']
        assert result['total_weight'] == backend_result['total_weight']
        assert abs(result['weighted_sum'] - backend_result['weighted_sum']) < 0.01
        assert abs(result['average_score'] - backend_result['average_score']) < 0.01
        
        # Verify pillar scores
        assert len(result['pillar_scores']) == len(backend_result['pillar_scores'])
        
        # With children, should have max score of 80 and total weight of 100
        assert result['max_possible_score'] == 80
        assert result['total_weight'] == 100
    
    def test_score_preview_without_children(self):
        """Test score preview API without children profile."""
        request_data = {
            'responses': self.base_responses,
            'profile': {'children': 'No'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify values match backend calculation
        backend_result = self.scorer.calculate_scores_v2(self.base_responses, {'children': 'No'})
        
        assert result['total_score'] == backend_result['total_score']
        assert result['max_possible_score'] == backend_result['max_possible_score']
        assert result['total_weight'] == backend_result['total_weight']
        
        # Without children, should have max score of 75 and total weight of 95
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_score_preview_no_profile(self):
        """Test score preview API with no profile (guest user)."""
        request_data = {
            'responses': self.base_responses,
            'profile': None
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_score_preview_empty_profile(self):
        """Test score preview API with empty profile."""
        request_data = {
            'responses': self.base_responses,
            'profile': {}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should default to no children behavior
        assert result['max_possible_score'] == 75
        assert result['total_weight'] == 95
    
    def test_score_preview_mixed_responses(self):
        """Test score preview API with mixed response values."""
        mixed_responses = {
            'q1_income_stability': 5,
            'q2_income_sources': 3,
            'q3_living_expenses': 4,
            'q4_budget_tracking': 2,
            'q5_spending_control': 4,
            'q6_expense_review': 3,
            'q7_savings_rate': 5,
            'q8_emergency_fund': 2,
            'q9_savings_optimization': 3,
            'q10_payment_history': 5,
            'q11_debt_ratio': 4,
            'q12_credit_score': 3,
            'q13_retirement_planning': 2,
            'q14_insurance_coverage': 4,
            'q15_financial_planning': 3,
            'q16_children_planning': 5
        }
        
        request_data = {
            'responses': mixed_responses,
            'profile': {'children': 'Yes'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify consistency with backend
        backend_result = self.scorer.calculate_scores_v2(mixed_responses, {'children': 'Yes'})
        
        assert result['total_score'] == backend_result['total_score']
        assert result['max_possible_score'] == backend_result['max_possible_score']
        assert result['total_weight'] == backend_result['total_weight']
    
    def test_score_preview_edge_cases(self):
        """Test score preview API with edge case values."""
        # All minimum values
        min_responses = {k: 1 for k in self.base_responses.keys()}
        
        request_data = {
            'responses': min_responses,
            'profile': {'children': 'No'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should get minimum score (15)
        assert result['total_score'] == 15
        
        # All maximum values
        max_responses = {k: 5 for k in self.base_responses.keys()}
        
        request_data = {
            'responses': max_responses,
            'profile': {'children': 'Yes'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should get maximum score (80 with children)
        assert result['total_score'] == 80
    
    def test_score_preview_validation_errors(self):
        """Test score preview API validation errors."""
        # Empty responses
        request_data = {
            'responses': {},
            'profile': None
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 422  # Validation error
        
        # Missing responses field
        request_data = {
            'profile': None
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_score_preview_pillar_structure(self):
        """Test that pillar scores have correct structure."""
        request_data = {
            'responses': self.base_responses,
            'profile': {'children': 'Yes'}
        }
        
        response = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify pillar structure
        pillar_scores = result['pillar_scores']
        assert len(pillar_scores) == 7  # 7 pillars
        
        for pillar in pillar_scores:
            assert 'factor' in pillar
            assert 'name' in pillar
            assert 'score' in pillar
            assert 'max_score' in pillar
            assert 'percentage' in pillar
            assert 'weight' in pillar
            
            # Verify data types and ranges
            assert isinstance(pillar['score'], (int, float))
            assert isinstance(pillar['max_score'], int)
            assert isinstance(pillar['percentage'], int)
            assert isinstance(pillar['weight'], int)
            
            assert 1 <= pillar['score'] <= 5
            assert pillar['max_score'] == 5
            assert 0 <= pillar['percentage'] <= 100
            assert pillar['weight'] > 0
    
    def test_score_preview_consistency_across_calls(self):
        """Test that multiple calls with same data return consistent results."""
        request_data = {
            'responses': self.base_responses,
            'profile': {'children': 'Yes'}
        }
        
        # Make multiple calls
        response1 = self.client.post('/surveys/calculate-preview', json=request_data)
        response2 = self.client.post('/surveys/calculate-preview', json=request_data)
        response3 = self.client.post('/surveys/calculate-preview', json=request_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        result1 = response1.json()
        result2 = response2.json()
        result3 = response3.json()
        
        # All results should be identical
        assert result1 == result2 == result3