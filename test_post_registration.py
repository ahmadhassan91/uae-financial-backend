#!/usr/bin/env python3
"""Test script for post-survey registration functionality."""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_post_registration():
    """Test the post-survey registration endpoint."""
    
    # Sample guest survey data (similar to what would be in localStorage)
    guest_survey_data = {
        "id": "guest-" + str(int(datetime.now().timestamp())),
        "userId": "guest-user",
        "profile": {
            "name": "John Doe",
            "age": 30,
            "gender": "Male",
            "nationality": "UAE",
            "children": "No",
            "employmentStatus": "Employed",
            "employmentSector": "Technology",
            "incomeRange": "AED 10,000 - 15,000",
            "emailAddress": "john.doe@example.com",
            "residence": "Dubai"
        },
        "responses": [
            {"questionId": "q1_income_stability", "value": 4},
            {"questionId": "q2_income_sources", "value": 3},
            {"questionId": "q3_monthly_expenses", "value": 4},
            {"questionId": "q4_expense_tracking", "value": 3},
            {"questionId": "q5_savings_habit", "value": 4}
        ],
        "totalScore": 65,
        "maxPossibleScore": 75,
        "pillarScores": [
            {
                "pillar": "income_stream",
                "score": 13,
                "maxScore": 15,
                "percentage": 87,
                "interpretation": "Good"
            },
            {
                "pillar": "savings_habit",
                "score": 12,
                "maxScore": 15,
                "percentage": 80,
                "interpretation": "Good"
            }
        ],
        "advice": [
            "Continue maintaining your good income stability",
            "Consider increasing your emergency fund"
        ],
        "createdAt": datetime.now().isoformat(),
        "modelVersion": "v2"
    }
    
    # Registration request data
    registration_data = {
        "email": "john.doe.test@example.com",
        "dateOfBirth": "1993-05-15",
        "guestSurveyData": guest_survey_data,
        "subscribeToUpdates": True
    }
    
    try:
        print("Testing post-survey registration...")
        print(f"API URL: {API_BASE_URL}/auth/post-register")
        
        # Make the registration request
        response = requests.post(
            f"{API_BASE_URL}/auth/post-register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {result['user_id']}")
            print(f"Email: {result['email']}")
            print(f"Session ID: {result['session_id']}")
            print(f"Survey History Count: {len(result['survey_history'])}")
            print(f"Session Expires: {result['expires_at']}")
            
            # Test duplicate registration (should handle gracefully)
            print("\nTesting duplicate registration...")
            duplicate_response = requests.post(
                f"{API_BASE_URL}/auth/post-register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if duplicate_response.status_code == 200:
                print("✅ Duplicate registration handled correctly")
            else:
                print(f"❌ Duplicate registration failed: {duplicate_response.text}")
            
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


def test_invalid_data():
    """Test registration with invalid data."""
    print("\nTesting invalid data scenarios...")
    
    # Test with missing required fields
    invalid_data = {
        "email": "invalid@example.com",
        "dateOfBirth": "1990-01-01",
        "guestSurveyData": {},  # Missing required fields
        "subscribeToUpdates": False
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/post-register",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid data properly rejected")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid data test failed: {e}")


if __name__ == "__main__":
    test_post_registration()
    test_invalid_data()
    print("\nPost-registration tests completed!")