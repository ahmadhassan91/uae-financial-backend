#!/usr/bin/env python3
"""
Test script to validate the current backend scoring implementation 
against the official assessment methodology shown in the provided images.

This script will:
1. Test the scoring logic with sample responses
2. Validate pillar calculations match the official methodology
3. Check if the percentage calculations are correct
4. Identify any discrepancies in the implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.surveys.scoring import SurveyScorer
import json

def test_official_scoring_methodology():
    """Test the scoring against the official methodology from the images."""
    
    print("🧪 Testing Official Scoring Methodology")
    print("=" * 60)
    
    scorer = SurveyScorer()
    
    # Test case 1: Sample responses based on the official methodology
    # Using mid-range scores (3 = Neutral) for all questions
    sample_responses = {
        # Income Stream (20% total weight)
        'q1_income_stability': 3,      # 10% weight
        'q2_income_sources': 3,        # 10% weight
        
        # Monthly Expenses Management (25% total weight)  
        'q3_living_expenses': 3,       # 10% weight
        'q4_budget_tracking': 3,       # 5% weight
        'q5_spending_control': 3,      # 5% weight
        'q6_expense_review': 3,        # 5% weight
        
        # Savings Habit (15% total weight)
        'q7_savings_rate': 3,          # 5% weight
        'q8_emergency_fund': 3,        # 5% weight
        'q9_savings_optimization': 3,  # 5% weight
        
        # Debt Management (15% total weight)
        'q10_payment_history': 3,      # 5% weight
        'q11_debt_ratio': 3,           # 5% weight
        'q12_credit_score': 3,         # 5% weight
        
        # Retirement Planning (10% total weight)
        'q13_retirement_planning': 3,  # 10% weight
        
        # Protection (5% total weight)
        'q14_insurance_coverage': 3,   # 5% weight
        
        # Future Planning (5% base weight)
        'q15_financial_planning': 3,   # 5% weight
        # q16 not included for users without children
    }
    
    # Test without children (should be 75% total weight, max score 75)
    print("\n📊 Test Case 1: User WITHOUT children")
    print("-" * 40)
    
    profile_no_children = {'children': 'No'}
    result_no_children = scorer.calculate_scores_v2(sample_responses, profile_no_children)
    
    print(f"Total Score: {result_no_children['total_score']}")
    print(f"Max Possible Score: {result_no_children['max_possible_score']}")
    print(f"Weighted Sum: {result_no_children.get('weighted_sum', 'N/A')}")
    print(f"Total Weight: {result_no_children.get('total_weight', 'N/A')}")
    
    print("\nPillar Breakdown:")
    for pillar in result_no_children['pillar_scores']:
        print(f"  {pillar['name']}: {pillar['score']}/{pillar['max_score']} = {pillar['percentage']}% (Weight: {pillar.get('weight', 'N/A')}%)")
    
    # Test with children (should include Q16, max score 80)
    print("\n📊 Test Case 2: User WITH children")
    print("-" * 40)
    
    sample_responses_with_children = sample_responses.copy()
    sample_responses_with_children['q16_children_planning'] = 3  # 5% weight
    
    profile_with_children = {'children': 'Yes'}
    result_with_children = scorer.calculate_scores_v2(sample_responses_with_children, profile_with_children)
    
    print(f"Total Score: {result_with_children['total_score']}")
    print(f"Max Possible Score: {result_with_children['max_possible_score']}")
    print(f"Weighted Sum: {result_with_children.get('weighted_sum', 'N/A')}")
    print(f"Total Weight: {result_with_children.get('total_weight', 'N/A')}")
    
    print("\nPillar Breakdown:")
    for pillar in result_with_children['pillar_scores']:
        print(f"  {pillar['name']}: {pillar['score']}/{pillar['max_score']} = {pillar['percentage']}% (Weight: {pillar.get('weight', 'N/A')}%)")
    
    # Test case 3: High scores (should show proper percentages)
    print("\n📊 Test Case 3: High scores (4/5)")
    print("-" * 40)
    
    high_responses = {k: 4 for k in sample_responses.keys()}
    result_high = scorer.calculate_scores_v2(high_responses, profile_no_children)
    
    print(f"Total Score: {result_high['total_score']}")
    print(f"Max Possible Score: {result_high['max_possible_score']}")
    
    print("\nPillar Breakdown (High Scores):")
    for pillar in result_high['pillar_scores']:
        expected_percentage = (4/5) * 100  # Should be 80%
        print(f"  {pillar['name']}: {pillar['score']}/{pillar['max_score']} = {pillar['percentage']}% (Expected: {expected_percentage}%)")
        
        if pillar['percentage'] != expected_percentage:
            print(f"    ❌ MISMATCH! Expected {expected_percentage}%, got {pillar['percentage']}%")
        else:
            print(f"    ✅ Correct percentage")
    
    # Validate the official methodology
    print("\n🔍 Methodology Validation")
    print("-" * 40)
    
    # Check question weights
    expected_weights = {
        'q1_income_stability': 10,
        'q2_income_sources': 10,
        'q3_living_expenses': 10,
        'q4_budget_tracking': 5,
        'q5_spending_control': 5,
        'q6_expense_review': 5,
        'q7_savings_rate': 5,
        'q8_emergency_fund': 5,
        'q9_savings_optimization': 5,
        'q10_payment_history': 5,
        'q11_debt_ratio': 5,
        'q12_credit_score': 5,
        'q13_retirement_planning': 10,
        'q14_insurance_coverage': 5,
        'q15_financial_planning': 5,
        'q16_children_planning': 5
    }
    
    print("Question Weight Validation:")
    for q_id, expected_weight in expected_weights.items():
        actual_weight = scorer.get_question_weight(q_id)
        if actual_weight == expected_weight:
            print(f"  ✅ {q_id}: {actual_weight}% (correct)")
        else:
            print(f"  ❌ {q_id}: Expected {expected_weight}%, got {actual_weight}%")
    
    # Check pillar weight totals
    print("\nPillar Weight Validation:")
    expected_pillar_weights = {
        'income_stream': 20,
        'monthly_expenses': 25,
        'savings_habit': 15,
        'debt_management': 15,
        'retirement_planning': 10,
        'protection': 5,
        'future_planning': 5  # 10 with children
    }
    
    for pillar, expected_weight in expected_pillar_weights.items():
        actual_weight_no_children = scorer.get_pillar_weight_calculation(pillar, False)
        actual_weight_with_children = scorer.get_pillar_weight_calculation(pillar, True)
        
        if pillar == 'future_planning':
            print(f"  {pillar}:")
            print(f"    Without children: {actual_weight_no_children}% (expected: 5%)")
            print(f"    With children: {actual_weight_with_children}% (expected: 10%)")
        else:
            if actual_weight_no_children == expected_weight:
                print(f"  ✅ {pillar}: {actual_weight_no_children}% (correct)")
            else:
                print(f"  ❌ {pillar}: Expected {expected_weight}%, got {actual_weight_no_children}%")
    
    # Check total weights
    total_weight_no_children = scorer.get_total_possible_weight(False)
    total_weight_with_children = scorer.get_total_possible_weight(True)
    
    print(f"\nTotal Weight Validation:")
    print(f"  Without children: {total_weight_no_children}% (expected: 75%)")
    print(f"  With children: {total_weight_with_children}% (expected: 80%)")
    
    if total_weight_no_children != 75:
        print(f"  ❌ Total weight without children should be 75%, got {total_weight_no_children}%")
    else:
        print(f"  ✅ Total weight without children is correct")
        
    if total_weight_with_children != 80:
        print(f"  ❌ Total weight with children should be 80%, got {total_weight_with_children}%")
    else:
        print(f"  ✅ Total weight with children is correct")

def test_score_range_validation():
    """Test that scores fall within the expected 15-75/80 range."""
    
    print("\n🎯 Score Range Validation")
    print("-" * 40)
    
    scorer = SurveyScorer()
    
    # Test minimum scores (all 1s)
    min_responses = {
        'q1_income_stability': 1, 'q2_income_sources': 1,
        'q3_living_expenses': 1, 'q4_budget_tracking': 1, 'q5_spending_control': 1, 'q6_expense_review': 1,
        'q7_savings_rate': 1, 'q8_emergency_fund': 1, 'q9_savings_optimization': 1,
        'q10_payment_history': 1, 'q11_debt_ratio': 1, 'q12_credit_score': 1,
        'q13_retirement_planning': 1, 'q14_insurance_coverage': 1, 'q15_financial_planning': 1
    }
    
    min_result = scorer.calculate_scores_v2(min_responses, {'children': 'No'})
    print(f"Minimum score (all 1s): {min_result['total_score']} (expected: 15)")
    
    # Test maximum scores (all 5s)
    max_responses = {k: 5 for k in min_responses.keys()}
    max_result = scorer.calculate_scores_v2(max_responses, {'children': 'No'})
    print(f"Maximum score (all 5s): {max_result['total_score']} (expected: 75)")
    
    # Test with children
    max_responses_children = max_responses.copy()
    max_responses_children['q16_children_planning'] = 5
    max_result_children = scorer.calculate_scores_v2(max_responses_children, {'children': 'Yes'})
    print(f"Maximum score with children (all 5s): {max_result_children['total_score']} (expected: 80)")

if __name__ == "__main__":
    test_official_scoring_methodology()
    test_score_range_validation()
    
    print("\n" + "=" * 60)
    print("🏁 Testing Complete")
    print("=" * 60)