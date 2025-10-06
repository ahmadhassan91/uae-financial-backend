"""
Test script for the Dynamic Question API endpoints.

This script tests the REST API endpoints for dynamic question selection.
"""
import requests
import json
from datetime import datetime


def test_api_endpoints():
    """Test the dynamic question API endpoints."""
    base_url = "http://localhost:8000"
    
    print("Testing Dynamic Question API Endpoints")
    print("=" * 50)
    
    # Test 1: Populate sample data
    print("\n1. Populating sample data...")
    try:
        response = requests.post(f"{base_url}/api/dynamic-questions/populate-sample-data")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sample data populated: {result}")
        else:
            print(f"✗ Failed to populate sample data: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error populating sample data: {e}")
    
    # Test 2: Get demographic rules
    print("\n2. Getting demographic rules...")
    try:
        response = requests.get(f"{base_url}/api/dynamic-questions/rules")
        if response.status_code == 200:
            rules = response.json()
            print(f"✓ Found {len(rules)} demographic rules")
            for rule in rules[:3]:  # Show first 3
                print(f"  - {rule['name']} (Priority: {rule['priority']})")
        else:
            print(f"✗ Failed to get rules: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting rules: {e}")
    
    # Test 3: Get question variations
    print("\n3. Getting question variations...")
    try:
        response = requests.get(f"{base_url}/api/dynamic-questions/variations")
        if response.status_code == 200:
            variations = response.json()
            print(f"✓ Found {len(variations)} question variations")
            for var in variations[:3]:  # Show first 3
                print(f"  - {var['base_question_id']}: {var['variation_name']} ({var['language']})")
        else:
            print(f"✗ Failed to get variations: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting variations: {e}")
    
    # Test 4: Validate a rule
    print("\n4. Validating a demographic rule...")
    try:
        test_rule = {
            "conditions": {
                "and": [
                    {"nationality": {"eq": "UAE"}},
                    {"age": {"gte": 25}}
                ]
            },
            "actions": {
                "include_questions": ["q1_income_stability", "q2_income_sources"]
            }
        }
        
        response = requests.post(
            f"{base_url}/api/dynamic-questions/rules/validate",
            json=test_rule
        )
        
        if response.status_code == 200:
            validation = response.json()
            print(f"✓ Rule validation: Valid={validation['valid']}")
            if validation['errors']:
                print(f"  Errors: {validation['errors']}")
            if validation['warnings']:
                print(f"  Warnings: {validation['warnings']}")
        else:
            print(f"✗ Failed to validate rule: {response.status_code}")
    except Exception as e:
        print(f"✗ Error validating rule: {e}")
    
    # Test 5: Get analytics
    print("\n5. Getting analytics...")
    try:
        response = requests.get(f"{base_url}/api/dynamic-questions/analytics")
        if response.status_code == 200:
            analytics = response.json()
            print(f"✓ Analytics retrieved:")
            print(f"  - Active rules: {analytics['total_active_rules']}")
            print(f"  - Active variations: {analytics['total_active_variations']}")
            print(f"  - Variations by language: {analytics['variations_by_language']}")
        else:
            print(f"✗ Failed to get analytics: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting analytics: {e}")
    
    # Test 6: Create a test customer profile and get questions
    print("\n6. Testing question selection (requires existing customer profile)...")
    print("Note: This test requires a customer profile to exist in the database.")
    print("You can create one through the regular customer API or use profile ID 1 if it exists.")
    
    # Try to get questions for profile ID 1
    try:
        profile_id = 1
        response = requests.get(
            f"{base_url}/api/dynamic-questions/questions/{profile_id}",
            params={
                "strategy": "hybrid",
                "language": "en"
            }
        )
        
        if response.status_code == 200:
            question_set = response.json()
            print(f"✓ Got {question_set['total_questions']} questions for profile {profile_id}")
            print(f"  - Strategy used: {question_set['strategy_used']}")
            print(f"  - Variations used: {len(question_set['variations_used'])}")
            print(f"  - First question: {question_set['questions'][0]['text'][:60]}...")
        elif response.status_code == 404:
            print(f"ℹ Customer profile {profile_id} not found (expected if no profiles exist)")
        else:
            print(f"✗ Failed to get questions: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error getting questions: {e}")
    
    # Test 7: Analyze demographic profile
    try:
        profile_id = 1
        response = requests.get(f"{base_url}/api/dynamic-questions/analyze/{profile_id}")
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"✓ Demographic analysis for profile {profile_id}:")
            matched_rules = [r for r in analysis['matched_rules'] if r['matched']]
            print(f"  - Matched rules: {len(matched_rules)}")
            print(f"  - Selected questions: {len(analysis['selected_questions'])}")
            print(f"  - Added questions: {len(analysis['added_questions'])}")
        elif response.status_code == 404:
            print(f"ℹ Customer profile {profile_id} not found for analysis")
        else:
            print(f"✗ Failed to analyze profile: {response.status_code}")
    except Exception as e:
        print(f"✗ Error analyzing profile: {e}")
    
    print("\n" + "=" * 50)
    print("API endpoint testing completed!")
    print("\nTo test with real customer profiles:")
    print("1. Create a customer profile using the customer API")
    print("2. Use the profile ID in the questions and analyze endpoints")
    print("3. Try different strategies: default, demographic, company, hybrid")


if __name__ == "__main__":
    test_api_endpoints()