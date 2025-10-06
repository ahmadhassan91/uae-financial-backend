#!/usr/bin/env python3
"""
Test script for simple authentication functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_simple_auth():
    """Test the simple authentication endpoint"""
    
    # First, let's register a user to test with
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    print("1. Registering test user...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✓ User registered successfully")
            user_data = response.json()
            print(f"  User ID: {user_data['id']}")
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print("✓ User already exists, continuing with test")
        else:
            print(f"✗ Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ Registration error: {e}")
        return
    
    # Test simple authentication
    simple_auth_data = {
        "email": "test@example.com",
        "dateOfBirth": "1990-01-01"
    }
    
    print("\n2. Testing simple authentication...")
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=simple_auth_data)
        if response.status_code == 200:
            print("✓ Simple authentication successful")
            auth_response = response.json()
            print(f"  User ID: {auth_response['user_id']}")
            print(f"  Email: {auth_response['email']}")
            print(f"  Session ID: {auth_response['session_id']}")
            print(f"  Survey History: {len(auth_response['survey_history'])} items")
            print(f"  Expires At: {auth_response['expires_at']}")
            return auth_response
        else:
            print(f"✗ Simple authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Simple authentication error: {e}")
        return None

def test_invalid_auth():
    """Test simple authentication with invalid credentials"""
    
    print("\n3. Testing invalid authentication...")
    
    # Test with wrong date of birth
    invalid_data = {
        "email": "test@example.com",
        "dateOfBirth": "1985-05-15"  # Different date
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=invalid_data)
        if response.status_code == 401:
            print("✓ Invalid credentials properly rejected")
        else:
            print(f"✗ Expected 401, got {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Invalid auth test error: {e}")
    
    # Test with non-existent email
    invalid_data = {
        "email": "nonexistent@example.com",
        "dateOfBirth": "1990-01-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/simple-login", json=invalid_data)
        if response.status_code == 401:
            print("✓ Non-existent email properly rejected")
        else:
            print(f"✗ Expected 401, got {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Non-existent email test error: {e}")

if __name__ == "__main__":
    print("Testing Simple Authentication System")
    print("=" * 40)
    
    # Test valid authentication
    auth_result = test_simple_auth()
    
    # Test invalid authentication
    test_invalid_auth()
    
    print("\n" + "=" * 40)
    print("Simple authentication tests completed!")