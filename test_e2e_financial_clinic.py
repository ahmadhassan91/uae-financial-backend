#!/usr/bin/env python3
"""
End-to-End Test Script for Financial Clinic Complete Flow
Tests: Profile → Survey → Results → PDF Download → Email Send → History
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Test user data
TEST_USER = {
    "email": "test_user_" + str(int(time.time())) + "@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
}

# Financial Clinic profile data
PROFILE_DATA = {
    "name": "Ahmed Mohamed",
    "age": 35,
    "nationality": "uae_national",
    "emirate": "dubai",
    "monthly_income": "15000-30000",
    "occupation": "professional",
    "dependents": 2
}

# Financial Clinic answers (matching the 16 questions)
ANSWERS = {
    "fc_q1": "stable",
    "fc_q2": "20_percent_or_more",
    "fc_q3": "three_to_six_months",
    "fc_q4": "within_my_means",
    "fc_q5": "regularly",
    "fc_q6": "manageable",
    "fc_q7": "yes_with_plan",
    "fc_q8": "yes",
    "fc_q9": "yes_diversified",
    "fc_q10": "adequate",
    "fc_q11": "yes",
    "fc_q12": "moderate",
    "fc_q13": "regularly",
    "fc_q14": "at_least_annually",
    "fc_q15": "yes",
    "fc_q16": "low_to_moderate"
}


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(success, message):
    """Print a formatted result."""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def test_1_guest_submit_survey():
    """Test 1: Guest user submits Financial Clinic survey."""
    print_section("TEST 1: Guest Submit Financial Clinic Survey")
    
    try:
        # Submit as guest (no user_id)
        payload = {
            "profile": PROFILE_DATA,
            "answers": ANSWERS
        }
        
        print("📤 Submitting survey as guest...")
        response = requests.post(
            f"{API_URL}/financial-clinic/submit",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Survey submitted successfully")
            print(f"   Total Score: {data['result']['total_score']:.1f}/100")
            print(f"   Status: {data['result']['status_band']}")
            print(f"   Categories: {len(data['result']['category_scores'])}")
            print(f"   Response ID: {data.get('response_id', 'N/A')}")
            return data
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_2_download_pdf(result_data):
    """Test 2: Download PDF report."""
    print_section("TEST 2: Download PDF Report")
    
    try:
        payload = {
            "result": result_data['result'],
            "profile": result_data['profile'],
            "language": "en"
        }
        
        print("📥 Requesting PDF download...")
        response = requests.post(
            f"{API_URL}/financial-clinic/report/pdf",
            json=payload
        )
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            # Save PDF
            filename = f"test_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_result(True, "PDF downloaded successfully")
            print(f"   File size: {len(response.content):,} bytes")
            print(f"   Saved as: {filename}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                print(f"   Response: {response.json()}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_3_send_email(result_data):
    """Test 3: Send email report (will show configuration message if SMTP not set up)."""
    print_section("TEST 3: Send Email Report")
    
    try:
        payload = {
            "email": TEST_USER["email"],
            "result": result_data['result'],
            "profile": result_data['profile'],
            "language": "en"
        }
        
        print(f"📧 Sending email to {TEST_USER['email']}...")
        response = requests.post(
            f"{API_URL}/financial-clinic/report/email",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(data.get('success', False), data.get('message', 'Unknown'))
            if not data.get('success'):
                print(f"   Note: {data.get('note', 'Email service not configured')}")
            return data.get('success', False)
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_4_create_account():
    """Test 4: Guest creates an account."""
    print_section("TEST 4: Create Account")
    
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        print(f"👤 Creating account for {TEST_USER['email']}...")
        response = requests.post(
            f"{API_URL}/auth/simple-register",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Account created successfully")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            TEST_USER['id'] = data.get('user', {}).get('id')
            TEST_USER['token'] = data.get('access_token')
            return data
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_5_authenticated_submit():
    """Test 5: Authenticated user submits another survey."""
    print_section("TEST 5: Authenticated User Submit Survey")
    
    try:
        # Modified answers for second submission
        modified_answers = ANSWERS.copy()
        modified_answers["fc_q2"] = "10_to_20_percent"  # Lower savings rate
        
        payload = {
            "profile": PROFILE_DATA,
            "answers": modified_answers
        }
        
        headers = {
            "Authorization": f"Bearer {TEST_USER.get('token', '')}"
        }
        
        print("📤 Submitting survey as authenticated user...")
        response = requests.post(
            f"{API_URL}/financial-clinic/submit",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Survey submitted successfully")
            print(f"   Total Score: {data['result']['total_score']:.1f}/100")
            print(f"   Response ID: {data.get('response_id', 'N/A')}")
            return data
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_6_view_history():
    """Test 6: View Financial Clinic history."""
    print_section("TEST 6: View History")
    
    try:
        headers = {
            "Authorization": f"Bearer {TEST_USER.get('token', '')}"
        }
        
        print("📜 Fetching Financial Clinic history...")
        response = requests.get(
            f"{API_URL}/financial-clinic/history",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assessments = data.get('assessments', [])
            print_result(True, f"History retrieved: {len(assessments)} assessment(s)")
            
            for i, assessment in enumerate(assessments, 1):
                print(f"\n   Assessment {i}:")
                print(f"     Date: {assessment.get('completed_at', 'N/A')}")
                print(f"     Score: {assessment.get('overall_score', 'N/A')}/100")
                print(f"     Status: {assessment.get('status_band', 'N/A')}")
            
            return data
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_7_download_historical_pdf(history_data):
    """Test 7: Download PDF from history."""
    print_section("TEST 7: Download Historical PDF")
    
    try:
        assessments = history_data.get('assessments', [])
        if not assessments:
            print_result(False, "No assessments in history")
            return False
        
        response_id = assessments[0].get('id')
        
        payload = {
            "survey_response_id": response_id,
            "language": "en"
        }
        
        headers = {
            "Authorization": f"Bearer {TEST_USER.get('token', '')}"
        }
        
        print(f"📥 Downloading PDF for response ID: {response_id}...")
        response = requests.post(
            f"{API_URL}/financial-clinic/report/pdf",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            filename = f"test_historical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_result(True, "Historical PDF downloaded successfully")
            print(f"   File size: {len(response.content):,} bytes")
            print(f"   Saved as: {filename}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def print_final_summary(results):
    """Print final test summary."""
    print_section("FINAL TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"\n📊 Tests Run: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%")
    
    print("\n" + "="*70)


def main():
    """Run all end-to-end tests."""
    print("\n" + "="*70)
    print("  FINANCIAL CLINIC - END-TO-END TEST SUITE")
    print("  Testing Complete User Journey")
    print("="*70)
    print(f"\n🌐 API URL: {API_URL}")
    print(f"📧 Test Email: {TEST_USER['email']}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Guest submits survey
    result_data = test_1_guest_submit_survey()
    results.append(result_data is not None)
    
    if result_data:
        # Test 2: Download PDF
        results.append(test_2_download_pdf(result_data))
        
        # Test 3: Send email
        results.append(test_3_send_email(result_data))
    else:
        results.extend([False, False])
    
    # Test 4: Create account
    time.sleep(1)  # Small delay
    account_data = test_4_create_account()
    results.append(account_data is not None)
    
    if account_data and TEST_USER.get('token'):
        # Test 5: Authenticated submit
        time.sleep(1)
        results.append(test_5_authenticated_submit() is not None)
        
        # Test 6: View history
        time.sleep(1)
        history_data = test_6_view_history()
        results.append(history_data is not None)
        
        # Test 7: Download historical PDF
        if history_data:
            results.append(test_7_download_historical_pdf(history_data))
        else:
            results.append(False)
    else:
        results.extend([False, False, False])
    
    # Print summary
    print_final_summary(results)
    
    print("\n💡 Tips:")
    print("   - Check generated PDF files to verify layout and content")
    print("   - Configure SMTP settings to test actual email delivery")
    print("   - Open browser to http://localhost:3000/financial-clinic to test UI")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
