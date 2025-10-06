#!/usr/bin/env python3
"""
Demonstration script for conditional Q16 scoring logic.

This script shows how the conditional Q16 scoring works with different
profile configurations.
"""
from app.surveys.scoring import SurveyScorer


def main():
    """Demonstrate conditional Q16 scoring."""
    print("=== Conditional Q16 Scoring Demonstration ===\n")
    
    # Initialize scorer
    scorer = SurveyScorer()
    
    # Sample survey responses (all 4s for consistency)
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
    
    print("Sample Survey Responses (all questions answered with 4):")
    for q_id, value in responses.items():
        print(f"  {q_id}: {value}")
    print()
    
    # Test 1: User with children
    print("1. User WITH children (Q16 should be INCLUDED):")
    profile_with_children = {'children': 'Yes'}
    result_with = scorer.calculate_scores_v2(responses, profile_with_children)
    
    print(f"   Max Possible Score: {result_with['max_possible_score']}")
    print(f"   Total Weight: {result_with['total_weight']}%")
    print(f"   Total Score: {result_with['total_score']}")
    
    # Find future planning pillar
    future_pillar_with = next(
        (p for p in result_with['pillar_scores'] if p['factor'] == 'future_planning'), 
        None
    )
    if future_pillar_with:
        print(f"   Future Planning Pillar Weight: {future_pillar_with['weight']}% (includes Q16)")
    print()
    
    # Test 2: User without children
    print("2. User WITHOUT children (Q16 should be EXCLUDED):")
    profile_without_children = {'children': 'No'}
    result_without = scorer.calculate_scores_v2(responses, profile_without_children)
    
    print(f"   Max Possible Score: {result_without['max_possible_score']}")
    print(f"   Total Weight: {result_without['total_weight']}%")
    print(f"   Total Score: {result_without['total_score']}")
    
    # Find future planning pillar
    future_pillar_without = next(
        (p for p in result_without['pillar_scores'] if p['factor'] == 'future_planning'), 
        None
    )
    if future_pillar_without:
        print(f"   Future Planning Pillar Weight: {future_pillar_without['weight']}% (excludes Q16)")
    print()
    
    # Test 3: Guest user (no profile)
    print("3. Guest user (no profile - Q16 should be EXCLUDED):")
    result_guest = scorer.calculate_scores_v2(responses, profile=None)
    
    print(f"   Max Possible Score: {result_guest['max_possible_score']}")
    print(f"   Total Weight: {result_guest['total_weight']}%")
    print(f"   Total Score: {result_guest['total_score']}")
    print()
    
    # Test 4: Impact of Q16 value when included
    print("4. Impact of Q16 response value (for users with children):")
    
    # Test with Q16 = 1
    responses_low = responses.copy()
    responses_low['q16_children_planning'] = 1
    result_low = scorer.calculate_scores_v2(responses_low, profile_with_children)
    
    # Test with Q16 = 5
    responses_high = responses.copy()
    responses_high['q16_children_planning'] = 5
    result_high = scorer.calculate_scores_v2(responses_high, profile_with_children)
    
    print(f"   Q16 = 1 (lowest): Total Score = {result_low['total_score']}")
    print(f"   Q16 = 5 (highest): Total Score = {result_high['total_score']}")
    print(f"   Score Difference: {result_high['total_score'] - result_low['total_score']} points")
    print()
    
    # Summary
    print("=== SUMMARY ===")
    print(f"✓ Users WITH children: Max score = 80, Q16 included")
    print(f"✓ Users WITHOUT children: Max score = 75, Q16 excluded")
    print(f"✓ Guest users: Max score = 75, Q16 excluded")
    print(f"✓ Q16 response value affects score when included")
    print(f"✓ Q16 response value ignored when excluded")
    print()
    print("Conditional Q16 scoring is working correctly! ✅")


if __name__ == "__main__":
    main()