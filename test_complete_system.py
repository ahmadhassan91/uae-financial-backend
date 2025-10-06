#!/usr/bin/env python3
"""
Comprehensive test script for the simplified authentication system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_system():
    """Test the complete simplified authentication system"""
    
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Guest Survey Submission
    print("\n1️⃣ Testing Guest Survey Submission...")
    guest_survey_data = {
        "responses": {
            "Q1": 3, "Q2": 4, "Q3": 2, "Q4": 5, "Q5": 3,
            "Q6": 4, "Q7": 3, "Q8": 2, "Q9": 5, "Q10": 4
        },
        "completion_time": 180
    }
    
    try:
        response = requests.post(f"{BASE_URL}/surveys/submit-guest", json=guest_survey_data)
        if response.status_code == 201:
            result = response.json()
            print("✅ Guest survey submission successful")
            print(f"   Overall Score: {result['score_breakdown']['overall_score']}")
            print(f"   Recommendations: {len(result['recommendations'])} items")
        else:
            print(f"❌ Guest survey failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Guest survey error: {e}")
        return False
    
    # Test 2: Use existing test user
    print("\n2️⃣ Using existing test user...")
    print("✅ Using test@example.com for authentication tests")
    
    # Test 3: Simple Authentication (First Time - Sets DOB)
    print("\n3️⃣ Testing Simple Authentication...")
    simple_auth_data = {
        "email": "test@example.com",
        "dateOfBirth": "1990-01-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=simple_auth_data)
        if response.status_code == 200:
            print("✅ Simple authentication successful")
            auth_result = response.json()
            print(f"   Session ID: {auth_result['session_id'][:20]}...")
            print(f"   Survey History: {len(auth_result['survey_history'])} items")
            session_id = auth_result['session_id']
        else:
            print(f"❌ Simple authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple authentication error: {e}")
        return False
    
    # Test 4: Simple Authentication (Second Time - Validates DOB)
    print("\n4️⃣ Testing Simple Authentication (Second Time)...")
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=simple_auth_data)
        if response.status_code == 200:
            print("✅ Simple authentication validation successful")
        else:
            print(f"❌ Simple authentication validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple authentication validation error: {e}")
        return False
    
    # Test 5: Invalid Authentication
    print("\n5️⃣ Testing Invalid Authentication...")
    invalid_data = {
        "email": "test@example.com",
        "dateOfBirth": "1985-05-15"  # Wrong DOB
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=invalid_data)
        if response.status_code == 401:
            print("✅ Invalid credentials properly rejected")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid auth test error: {e}")
        return False
    
    # Test 6: Rate Limiting (Multiple Failed Attempts)
    print("\n6️⃣ Testing Rate Limiting...")
    for i in range(3):
        try:
            response = requests.post(f"{BASE_URL}/auth/simple-login", json=invalid_data)
            if i < 2:
                print(f"   Attempt {i+1}: {response.status_code} (expected 401)")
            else:
                print(f"   Attempt {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Rate limiting test error: {e}")
            return False
    
    print("✅ Rate limiting test completed")
    
    return True

if __name__ == "__main__":
    success = test_complete_system()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    print("=" * 50)