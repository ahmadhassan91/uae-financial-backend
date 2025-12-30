#!/usr/bin/env python3
"""
Debug script for simple authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def debug_simple_auth():
    """Debug the simple authentication"""
    
    # Test with the exact date format
    simple_auth_data = {
        "email": "test@example.com",
        "dateOfBirth": "1990-01-01"
    }
    
    print("Debugging simple authentication...")
    print(f"Request data: {json.dumps(simple_auth_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=simple_auth_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("\nTrying with different date format...")
            # Try with different date format
            simple_auth_data["dateOfBirth"] = "1990-01-01T00:00:00"
            response2 = requests.post(f"{BASE_URL}/auth/simple-login", json=simple_auth_data)
            print(f"Status Code 2: {response2.status_code}")
            print(f"Response 2: {response2.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_simple_auth()