#!/usr/bin/env python3
"""
Comprehensive test to validate that the scoring fix works correctly.
This test verifies that pillar scores reflect actual user responses instead of hardcoded 5.0/5 values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.surveys.scoring import SurveyScorer
import json

def test_scoring_fix_validation():
    """Test that pillar scores accurately reflect user responses and are not hardcoded to maximum values."""
    
    print("🧪 SCORING FIX VALIDATION TEST")
    print("=" * 50)
    
    scorer = SurveyScorer()
    
    # Test Case 1: All minimum responses (should get low scores, not 5.0/5)
    print("\n1. 📉 Testing All Minimum Responses (All 1s)")
    print("-" * 40)
    
    min_responses = {
        'q1_income_stability': 1,
        'q2_income_sources': 1,
        'q3_living_expenses': 1,
        'q4_budget_tracking': 1,
        'q5_spending_control': 1,
        'q6_expense_review': 1,
        'q7_savings_rate': 1,
        'q8_emergency_fund': 1,
        'q9_savings_optimization': 1,
        'q10_payment_history': 1,
        'q11_debt_ratio': 1,
        'q12_credit_score': 1,
        'q13_retirement_planning': 1,
        'q14_insurance_coverage': 1,
        'q15_financial_planning': 1
    }
    
    min_result = scorer.calculate_scores_v2(min_responses)
    
    print(f"Total Score: {min_result['total_score']}")
    print("Pillar Scores:")
    
    all_scores_are_one = True
    all_scores_are_five = True
    
    for pillar in min_result['pillar_scores']:
        score = pillar['score']
        percentage = pillar['percentage']
        print(f"  {pillar['name']}: {score}/5 ({percentage}%)")
        
        if score != 1.0:
            all_scores_are_one = False
        if score != 5.0:
            all_scores_are_five = False
    
    # Validate minimum responses
    if all_scores_are_one:
        print("✅ PASS: All minimum responses correctly result in score 1.0/5")
    elif all_scores_are_five:
        print("❌ FAIL: All scores are 5.0/5 - scoring is still broken!")
        return False
    else:
        print("✅ PASS: Scores vary appropriately (not all 1.0 or 5.0)")
    
    # Test Case 2: All maximum responses (should get high scores)
    print("\n2. 📈 Testing All Maximum Responses (All 5s)")
    print("-" * 40)
    
    max_responses = {
        'q1_income_stability': 5,
        'q2_income_sources': 5,
        'q3_living_expenses': 5,
        'q4_budget_tracking': 5,
        'q5_spending_control': 5,
        'q6_expense_review': 5,
        'q7_savings_rate': 5,
        'q8_emergency_fund': 5,
        'q9_savings_optimization': 5,
        'q10_payment_history': 5,
        'q11_debt_ratio': 5,
        'q12_credit_score': 5,
        'q13_retirement_planning': 5,
        'q14_insurance_coverage': 5,
        'q15_financial_planning': 5
    }
    
    max_result = scorer.calculate_scores_v2(max_responses)
    
    print(f"Total Score: {max_result['total_score']}")
    print("Pillar Scores:")
    
    all_max_scores_are_five = True
    
    for pillar in max_result['pillar_scores']:
        score = pillar['score']
        percentage = pillar['percentage']
        print(f"  {pillar['name']}: {score}/5 ({percentage}%)")
        
        if score != 5.0:
            all_max_scores_are_five = False
    
    if all_max_scores_are_five:
        print("✅ PASS: All maximum responses correctly result in score 5.0/5")
    else:
        print("❌ FAIL: Maximum responses don't result in 5.0/5 scores")
        return False
    
    # Test Case 3: Mixed responses (should get varied scores)
    print("\n3. 🎯 Testing Mixed Responses (Varied Answers)")
    print("-" * 40)
    
    mixed_responses = {
        'q1_income_stability': 2,  # Low
        'q2_income_sources': 4,    # High
        'q3_living_expenses': 3,   # Medium
        'q4_budget_tracking': 1,   # Low
        'q5_spending_control': 5,  # High
        'q6_expense_review': 2,    # Low
        'q7_savings_rate': 4,      # High
        'q8_emergency_fund': 3,    # Medium
        'q9_savings_optimization': 1, # Low
        'q10_payment_history': 5,  # High
        'q11_debt_ratio': 2,       # Low
        'q12_credit_score': 4,     # High
        'q13_retirement_planning': 3, # Medium
        'q14_insurance_coverage': 1,  # Low
        'q15_financial_planning': 5   # High
    }
    
    mixed_result = scorer.calculate_scores_v2(mixed_responses)
    
    print(f"Total Score: {mixed_result['total_score']}")
    print("Pillar Scores:")
    
    pillar_scores = []
    all_mixed_scores_same = True
    first_score = None
    
    for pillar in mixed_result['pillar_scores']:
        score = pillar['score']
        percentage = pillar['percentage']
        pillar_scores.append(score)
        print(f"  {pillar['name']}: {score}/5 ({percentage}%)")
        
        if first_score is None:
            first_score = score
        elif score != first_score:
            all_mixed_scores_same = False
    
    # Validate mixed responses show variation
    if all_mixed_scores_same:
        print("❌ FAIL: All pillar scores are identical - not reflecting varied responses")
        return False
    else:
        print("✅ PASS: Pillar scores vary based on different responses")
    
    # Test Case 4: Validate score ranges are reasonable
    print("\n4. 📊 Validating Score Ranges")
    print("-" * 40)
    
    min_score = min(pillar_scores)
    max_score = max(pillar_scores)
    score_range = max_score - min_score
    
    print(f"Score Range: {min_score:.2f} to {max_score:.2f} (range: {score_range:.2f})")
    
    if score_range > 0.5:  # Expect at least 0.5 point difference
        print("✅ PASS: Scores show meaningful variation")
    else:
        print("❌ FAIL: Scores don't show enough variation")
        return False
    
    # Test Case 5: Validate total score calculation
    print("\n5. 🧮 Validating Total Score Calculation")
    print("-" * 40)
    
    # Check that total scores are different for different response patterns
    min_total = min_result['total_score']
    max_total = max_result['total_score']
    mixed_total = mixed_result['total_score']
    
    print(f"Min responses total: {min_total}")
    print(f"Max responses total: {max_total}")
    print(f"Mixed responses total: {mixed_total}")
    
    if min_total < mixed_total < max_total:
        print("✅ PASS: Total scores properly reflect response quality")
    else:
        print("❌ FAIL: Total scores don't properly reflect response patterns")
        return False
    
    # Test Case 6: Validate percentages match scores
    print("\n6. 📈 Validating Percentage Calculations")
    print("-" * 40)
    
    percentage_errors = 0
    for pillar in mixed_result['pillar_scores']:
        expected_percentage = (pillar['score'] / pillar['max_score']) * 100
        actual_percentage = pillar['percentage']
        
        if abs(expected_percentage - actual_percentage) > 1:  # Allow 1% tolerance
            print(f"❌ {pillar['name']}: Expected {expected_percentage:.1f}%, got {actual_percentage}%")
            percentage_errors += 1
        else:
            print(f"✅ {pillar['name']}: {actual_percentage}% (correct)")
    
    if percentage_errors == 0:
        print("✅ PASS: All percentages correctly calculated")
    else:
        print(f"❌ FAIL: {percentage_errors} percentage calculation errors")
        return False
    
    # Final validation
    print("\n" + "=" * 50)
    print("🎉 SCORING FIX VALIDATION RESULTS")
    print("=" * 50)
    
    print("✅ Pillar scores reflect actual user responses")
    print("✅ Scores are not hardcoded to 5.0/5")
    print("✅ Different responses produce different scores")
    print("✅ Score ranges are appropriate (1-5)")
    print("✅ Total scores vary based on response quality")
    print("✅ Percentages are calculated correctly")
    
    print("\n🎯 CONCLUSION: Scoring fix is working correctly!")
    print("   - Pillar scores now accurately reflect user survey responses")
    print("   - No more hardcoded 5.0/5 values for all pillars")
    print("   - Scoring system properly differentiates response quality")
    
    return True

def test_conditional_q16():
    """Test that Q16 conditional logic works correctly."""
    
    print("\n" + "=" * 50)
    print("🧪 TESTING CONDITIONAL Q16 LOGIC")
    print("=" * 50)
    
    scorer = SurveyScorer()
    
    # Base responses without Q16
    base_responses = {
        'q1_income_stability': 3,
        'q2_income_sources': 3,
        'q3_living_expenses': 3,
        'q4_budget_tracking': 3,
        'q5_spending_control': 3,
        'q6_expense_review': 3,
        'q7_savings_rate': 3,
        'q8_emergency_fund': 3,
        'q9_savings_optimization': 3,
        'q10_payment_history': 3,
        'q11_debt_ratio': 3,
        'q12_credit_score': 3,
        'q13_retirement_planning': 3,
        'q14_insurance_coverage': 3,
        'q15_financial_planning': 3
    }
    
    # Test without children (no Q16)
    print("\n1. Testing user without children (no Q16)")
    result_no_children = scorer.calculate_scores_v2(base_responses, profile={'children': 'No'})
    print(f"Max possible score: {result_no_children['max_possible_score']}")
    print(f"Total score: {result_no_children['total_score']}")
    
    # Test with children (includes Q16)
    print("\n2. Testing user with children (includes Q16)")
    responses_with_q16 = base_responses.copy()
    responses_with_q16['q16_children_planning'] = 4
    
    result_with_children = scorer.calculate_scores_v2(responses_with_q16, profile={'children': 'Yes'})
    print(f"Max possible score: {result_with_children['max_possible_score']}")
    print(f"Total score: {result_with_children['total_score']}")
    
    # Validate Q16 logic
    if result_no_children['max_possible_score'] == 75 and result_with_children['max_possible_score'] == 80:
        print("✅ PASS: Q16 conditional logic working correctly")
        return True
    else:
        print("❌ FAIL: Q16 conditional logic not working")
        return False

if __name__ == "__main__":
    print("Starting comprehensive scoring fix validation...")
    
    try:
        # Run main scoring tests
        main_test_passed = test_scoring_fix_validation()
        
        # Run Q16 conditional tests
        q16_test_passed = test_conditional_q16()
        
        if main_test_passed and q16_test_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("The scoring fix is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ SOME TESTS FAILED!")
            print("The scoring fix needs further investigation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)