"""
Test script to verify company-specific questions are loaded correctly
for company ID 12 in the score analytics table endpoint.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@nationalbonds.ae"
ADMIN_PASSWORD = "admin123"
COMPANY_ID = 11

def login():
    """Login and get admin token."""
    print("=" * 60)
    print("STEP 1: Admin Login")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✓ Login successful")
        print(f"  Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def get_company_info(token, company_id):
    """Get company information."""
    print("\n" + "=" * 60)
    print(f"STEP 2: Get Company {company_id} Information")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, let's see what companies exist
    response = requests.get(
        f"{BASE_URL}/api/v1/admin/simple/filter-options",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        companies = data.get("companies", [])
        print(f"✓ Found {len(companies)} companies:")
        
        target_company = None
        for company in companies:
            if company["id"] == company_id:
                target_company = company
                print(f"\n  TARGET COMPANY:")
                print(f"    ID: {company['id']}")
                print(f"    Name: {company['name']}")
                print(f"    URL: {company['unique_url']}")
            else:
                print(f"  - ID {company['id']}: {company['name']}")
        
        return target_company
    else:
        print(f"✗ Failed to get companies: {response.status_code}")
        return None

def check_variation_set(token, company_name):
    """Check if company has a variation set assigned."""
    print("\n" + "=" * 60)
    print("STEP 3: Check Variation Set Assignment")
    print("=" * 60)
    
    # This would require a database query, but we can infer from the API response
    print(f"  Checking if '{company_name}' has variation set...")
    print(f"  (This will be verified in the next step)")

def test_score_analytics_without_filter(token):
    """Test score analytics table WITHOUT company filter."""
    print("\n" + "=" * 60)
    print("STEP 4: Test Score Analytics (NO FILTER)")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/admin/simple/score-analytics-table",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful")
        print(f"\n  Response Structure:")
        print(f"    - question_set_type: {data.get('question_set_type')}")
        print(f"    - variation_set_name: {data.get('variation_set_name')}")
        print(f"    - filtered: {data.get('filtered')}")
        print(f"    - total_questions: {data.get('total_questions')}")
        
        if data.get('questions'):
            print(f"\n  First 3 Questions:")
            for q in data['questions'][:3]:
                print(f"    Q{q['question_number']}: {q['question_text'][:60]}...")
                print(f"      Category: {q['category']}")
        
        return data
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_score_analytics_with_company_filter(token, company_name):
    """Test score analytics table WITH company filter."""
    print("\n" + "=" * 60)
    print(f"STEP 5: Test Score Analytics (WITH COMPANY FILTER)")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with company name
    print(f"\n  Testing with company filter: '{company_name}'")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/admin/simple/score-analytics-table",
        headers=headers,
        params={"companies": company_name}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful")
        print(f"\n  Response Structure:")
        print(f"    - question_set_type: {data.get('question_set_type')}")
        print(f"    - variation_set_name: {data.get('variation_set_name')}")
        print(f"    - filtered: {data.get('filtered')}")
        print(f"    - total_questions: {data.get('total_questions')}")
        
        if data.get('error'):
            print(f"\n  ✗ ERROR: {data.get('error')}")
            if data.get('traceback'):
                print(f"\n  Traceback:")
                print(f"    {data.get('traceback')}")
        
        if data.get('questions'):
            print(f"\n  All Questions:")
            for q in data['questions']:
                print(f"    Q{q['question_number']}: {q['question_text'][:80]}...")
                print(f"      Category: {q['category']}")
                print(f"      Emirati: {q['emirati_count']} responses, avg: {q['emirati_avg']}")
                print(f"      Non-Emirati: {q['non_emirati_count']} responses, avg: {q['non_emirati_avg']}")
        else:
            print(f"\n  ✗ No questions returned!")
        
        return data
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def compare_results(without_filter, with_filter):
    """Compare the two results."""
    print("\n" + "=" * 60)
    print("STEP 6: COMPARISON")
    print("=" * 60)
    
    if not without_filter or not with_filter:
        print("  ✗ Cannot compare - one or both requests failed")
        return
    
    print(f"\n  WITHOUT Filter:")
    print(f"    - Question Set: {without_filter.get('question_set_type')}")
    print(f"    - Variation Set: {without_filter.get('variation_set_name')}")
    print(f"    - Total Questions: {without_filter.get('total_questions')}")
    
    print(f"\n  WITH Company Filter:")
    print(f"    - Question Set: {with_filter.get('question_set_type')}")
    print(f"    - Variation Set: {with_filter.get('variation_set_name')}")
    print(f"    - Total Questions: {with_filter.get('total_questions')}")
    
    # Check if questions are different
    if without_filter.get('questions') and with_filter.get('questions'):
        without_q1 = without_filter['questions'][0]['question_text'] if without_filter['questions'] else ""
        with_q1 = with_filter['questions'][0]['question_text'] if with_filter['questions'] else ""
        
        print(f"\n  First Question Comparison:")
        print(f"    Without Filter: {without_q1[:60]}...")
        print(f"    With Filter:    {with_q1[:60]}...")
        
        if without_q1 != with_q1:
            print(f"\n  ✓ Questions ARE DIFFERENT (company variations loaded!)")
        else:
            print(f"\n  ✗ Questions ARE THE SAME (company variations NOT loaded)")

def main():
    """Main test flow."""
    print("\n" + "=" * 70)
    print("COMPANY-SPECIFIC QUESTIONS TEST")
    print(f"Testing Company ID: {COMPANY_ID}")
    print("=" * 70)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n✗ Test failed: Could not login")
        return
    
    # Step 2: Get company info
    company = get_company_info(token, COMPANY_ID)
    if not company:
        print(f"\n✗ Test failed: Company {COMPANY_ID} not found")
        return
    
    company_name = company['name']
    
    # Step 3: Check variation set (informational)
    check_variation_set(token, company_name)
    
    # Step 4: Test without filter (baseline)
    without_filter = test_score_analytics_without_filter(token)
    
    # Step 5: Test with company filter
    with_filter = test_score_analytics_with_company_filter(token, company_name)
    
    # Step 6: Compare results
    compare_results(without_filter, with_filter)
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
