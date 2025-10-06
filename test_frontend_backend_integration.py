#!/usr/bin/env python3
"""
Test the actual API endpoint that the frontend calls to verify 
the data structure and values being returned.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.surveys.scoring import SurveyScorer
import json

def test_api_response_format():
    """Test the exact format returned by the API that frontend consumes."""
    
    print("🔌 Testing Frontend-Backend Integration")
    print("=" * 60)
    
    scorer = SurveyScorer()
    
    # Sample responses that would produce 3.75/5 = 75% for a pillar
    sample_responses = {
        'q1_income_stability': 4,      # High score
        'q2_income_sources': 3,        # Medium score
        # Average = 3.5, but let's test with mixed scores
        'q3_living_expenses': 4,
        'q4_budget_tracking': 4,
        'q5_spending_control': 3,
        'q6_expense_review': 4,
        'q7_savings_rate': 4,
        'q8_emergency_fund': 3,
        'q9_savings_optimization': 4,
        'q10_payment_history': 4,
        'q11_debt_ratio': 3,
        'q12_credit_score': 4,
        'q13_retirement_planning': 4,
        'q14_insurance_coverage': 3,
        'q15_financial_planning': 4,
    }
    
    result = scorer.calculate_scores_v2(sample_responses, {'children': 'No'})
    
    print("📊 API Response Structure:")
    print(json.dumps(result, indent=2))
    
    print("\n🔍 Pillar Score Analysis:")
    for pillar in result['pillar_scores']:
        score = pillar['score']
        max_score = pillar['max_score']
        percentage = pillar['percentage']
        calculated_percentage = (score / max_score) * 100
        
        print(f"\n{pillar['name']}:")
        print(f"  Raw Score: {score}/{max_score}")
        print(f"  Backend Percentage: {percentage}%")
        print(f"  Calculated Percentage: {calculated_percentage:.1f}%")
        print(f"  Match: {'✅' if abs(percentage - calculated_percentage) < 0.1 else '❌'}")
        
        # This is what frontend should display
        if score == 3.75:  # If we had a 3.75 score
            print(f"  Expected Frontend Display: 75% (not 15%)")

if __name__ == "__main__":
    test_api_response_format()