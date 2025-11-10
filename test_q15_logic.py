#!/usr/bin/env python3
"""
Test Question 15 (Q15) conditional logic.

Q15 is about children's education savings and should:
- Be SHOWN when children_count > 0
- Be HIDDEN when children_count == 0
- Get default score of 5 when hidden
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.surveys.financial_clinic_scoring import FinancialClinicScorer
from app.surveys.financial_clinic_questions import get_questions_for_profile


def test_q15_conditional_logic():
    """Test Q15 conditional logic comprehensively."""
    
    print("=" * 70)
    print("TESTING Q15 CONDITIONAL LOGIC")
    print("=" * 70)
    
    # Test 1: User WITHOUT children - Q15 should be excluded
    print("\n📝 Test 1: User WITHOUT children (children_count = 0)")
    print("-" * 70)
    
    children_count_0 = 0
    questions_0 = get_questions_for_profile(children_count=children_count_0)
    
    print(f"✓ Questions returned: {len(questions_0)}")
    print(f"  Expected: 14 questions (Q15 excluded)")
    
    q15_in_list = any(q.id == "fc_q15" for q in questions_0)
    print(f"✓ Q15 in question list: {q15_in_list}")
    print(f"  Expected: False")
    
    # Create responses WITHOUT Q15
    responses_no_children = {
        "fc_q1": 4, "fc_q2": 4, "fc_q3": 4, "fc_q4": 4,
        "fc_q5": 4, "fc_q6": 4, "fc_q7": 4, "fc_q8": 4,
        "fc_q9": 4, "fc_q10": 4, "fc_q11": 4, "fc_q12": 4,
        "fc_q13": 4, "fc_q14": 4
        # No fc_q15 in responses
    }
    
    scorer = FinancialClinicScorer()
    result_0 = scorer.calculate_score(responses_no_children, children_count=children_count_0)
    
    print(f"\n✓ Scoring Results:")
    print(f"  Total Score: {result_0.total_score}")
    print(f"  Total Questions: {result_0.total_questions}")
    print(f"  Questions Answered: {result_0.questions_answered}")
    print(f"  Expected: total_questions = 15 (Q15 auto-scored with 5)")
    
    # Check if Q15 got default score
    protecting_family_score = result_0.category_scores.get("Protecting Your Family")
    if protecting_family_score:
        print(f"\n✓ Protecting Your Family Category:")
        print(f"  Score: {protecting_family_score.score}")
        print(f"  Status: {protecting_family_score.status_level}")
        print(f"  Expected: Should include Q14 + Q15(default=5)")
    
    # Test 2: User WITH children - Q15 should be included
    print("\n" + "=" * 70)
    print("\n📝 Test 2: User WITH children (children_count = 2)")
    print("-" * 70)
    
    children_count_2 = 2
    questions_2 = get_questions_for_profile(children_count=children_count_2)
    
    print(f"✓ Questions returned: {len(questions_2)}")
    print(f"  Expected: 15 questions (Q15 included)")
    
    q15_in_list_2 = any(q.id == "fc_q15" for q in questions_2)
    print(f"✓ Q15 in question list: {q15_in_list_2}")
    print(f"  Expected: True")
    
    # Create responses WITH Q15
    responses_with_children = {
        "fc_q1": 4, "fc_q2": 4, "fc_q3": 4, "fc_q4": 4,
        "fc_q5": 4, "fc_q6": 4, "fc_q7": 4, "fc_q8": 4,
        "fc_q9": 4, "fc_q10": 4, "fc_q11": 4, "fc_q12": 4,
        "fc_q13": 4, "fc_q14": 4, "fc_q15": 3  # User provides answer
    }
    
    result_2 = scorer.calculate_score(responses_with_children, children_count=children_count_2)
    
    print(f"\n✓ Scoring Results:")
    print(f"  Total Score: {result_2.total_score}")
    print(f"  Total Questions: {result_2.total_questions}")
    print(f"  Questions Answered: {result_2.questions_answered}")
    print(f"  Expected: total_questions = 15, questions_answered = 15")
    
    # Check if Q15 used actual answer
    protecting_family_score_2 = result_2.category_scores.get("Protecting Your Family")
    if protecting_family_score_2:
        print(f"\n✓ Protecting Your Family Category:")
        print(f"  Score: {protecting_family_score_2.score}")
        print(f"  Status: {protecting_family_score_2.status_level}")
        print(f"  Expected: Should include Q14 + Q15(actual answer=3)")
    
    # Test 3: Verify scoring difference
    print("\n" + "=" * 70)
    print("\n📝 Test 3: Verify Q15 answer affects score")
    print("-" * 70)
    
    # Test with Q15 = 1 (worst)
    responses_q15_low = responses_with_children.copy()
    responses_q15_low["fc_q15"] = 1
    result_q15_low = scorer.calculate_score(responses_q15_low, children_count=2)
    
    # Test with Q15 = 5 (best)
    responses_q15_high = responses_with_children.copy()
    responses_q15_high["fc_q15"] = 5
    result_q15_high = scorer.calculate_score(responses_q15_high, children_count=2)
    
    print(f"✓ Score with Q15=1 (worst): {result_q15_low.total_score}")
    print(f"✓ Score with Q15=5 (best): {result_q15_high.total_score}")
    print(f"✓ Difference: {abs(result_q15_high.total_score - result_q15_low.total_score):.2f} points")
    print(f"  Expected: Scores should be different (Q15 affects result)")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    
    # Check Test 1
    test1_pass = (
        len(questions_0) == 14 and
        not q15_in_list and
        result_0.total_questions == 15
    )
    print(f"✓ Test 1 (No Children): {'PASS' if test1_pass else 'FAIL'}")
    all_passed = all_passed and test1_pass
    
    # Check Test 2
    test2_pass = (
        len(questions_2) == 15 and
        q15_in_list_2 and
        result_2.total_questions == 15 and
        result_2.questions_answered == 15
    )
    print(f"✓ Test 2 (With Children): {'PASS' if test2_pass else 'FAIL'}")
    all_passed = all_passed and test2_pass
    
    # Check Test 3
    test3_pass = result_q15_high.total_score != result_q15_low.total_score
    print(f"✓ Test 3 (Q15 Affects Score): {'PASS' if test3_pass else 'FAIL'}")
    all_passed = all_passed and test3_pass
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Q15 logic is working correctly!")
    else:
        print("❌ SOME TESTS FAILED! Q15 logic needs fixing!")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_q15_conditional_logic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
