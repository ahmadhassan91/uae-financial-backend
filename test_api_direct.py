#!/usr/bin/env python3
"""
Direct test of the API endpoints to verify they're working
"""

import requests
import json
import sys

def test_backend_api():
    """Test the backend API directly"""
    base_url = "http://localhost:8000"
    
    print("🔗 Testing Backend API Direct Connection")
    print(f"Base URL: {base_url}")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check successful")
            print(f"Response: {response.json()}")
        else:
            print("❌ Health check failed")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Root endpoint successful")
            print(f"Response: {response.json()}")
        else:
            print("❌ Root endpoint failed")
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: OPTIONS request to submit-guest
    print("\n3. Testing OPTIONS request to submit-guest...")
    try:
        response = requests.options(
            f"{base_url}/surveys/submit-guest",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        if response.status_code == 200:
            print("✅ OPTIONS request successful")
        else:
            print("❌ OPTIONS request failed")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ OPTIONS request error: {e}")
    
    # Test 4: POST request to submit-guest
    print("\n4. Testing POST request to submit-guest...")
    
    test_data = {
        "responses": {
            "q1": 3,
            "q2": 4,
            "q3": 2,
            "q4": 5,
            "q5": 3,
            "q6": 4,
            "q7": 2,
            "q8": 3,
            "q9": 4,
            "q10": 3,
            "q11": 2,
            "q12": 4,
            "q13": 3,
            "q14": 2,
            "q15": 4
        },
        "profile": {
            "name": "Test User",
            "age": 30,
            "nationality": "UAE National",
            "income_range": "10,000 - 20,000 AED",
            "employment_status": "Employed",
            "education_level": "Bachelor's Degree",
            "marital_status": "Single",
            "dependents": 0
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/surveys/submit-guest",
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000'
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        if response.status_code in [200, 201]:
            print("✅ POST request successful")
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            if 'total_score' in result:
                print(f"Total Score: {result['total_score']}")
        else:
            print("❌ POST request failed")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ POST request error: {e}")
    
    return True

if __name__ == "__main__":
    try:
        test_backend_api()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)