#!/usr/bin/env python3
"""Test script to verify FastAPI backend functionality."""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_user_registration():
    """Test user registration."""
    print("\n🔍 Testing user registration...")
    test_user = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            return user_data
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None

def test_user_login(email, password):
    """Test user login."""
    print("\n🔍 Testing user login...")
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            print(f"   Token type: {token_data['token_type']}")
            print(f"   Expires in: {token_data['expires_in']} seconds")
            return token_data['access_token']
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    print("\n🔍 Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            user_data = response.json()
            print(f"   User: {user_data['username']} ({user_data['email']})")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return False

def test_customer_profile_creation(token):
    """Test customer profile creation."""
    print("\n🔍 Testing customer profile creation...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_data = {
        "first_name": "Ahmed",
        "last_name": "Al-Mansoori",
        "age": 32,
        "gender": "male",
        "nationality": "UAE",
        "emirate": "dubai",
        "employment_status": "employed_full_time",
        "monthly_income": "15000_25000",
        "household_size": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/customers/profile", json=profile_data, headers=headers)
        if response.status_code == 201:
            print("✅ Customer profile creation successful")
            profile = response.json()
            print(f"   Profile ID: {profile['id']}")
            print(f"   Name: {profile['first_name']} {profile['last_name']}")
            return profile
        else:
            print(f"❌ Customer profile creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Customer profile creation error: {e}")
        return None

def main():
    """Run all tests."""
    print("🚀 Starting FastAPI Backend Tests")
    print("=" * 50)
    
    # Test basic endpoints
    if not test_health_check():
        sys.exit(1)
    
    if not test_root_endpoint():
        sys.exit(1)
    
    # Test authentication flow
    user_data = test_user_registration()
    if not user_data:
        sys.exit(1)
    
    token = test_user_login(user_data['email'], "testpassword123")
    if not token:
        sys.exit(1)
    
    if not test_protected_endpoint(token):
        sys.exit(1)
    
    # Test customer profile
    profile = test_customer_profile_creation(token)
    if not profile:
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! FastAPI backend is working correctly.")
    print("\n📊 Summary:")
    print("   ✅ Health check endpoint")
    print("   ✅ Root endpoint")
    print("   ✅ User registration")
    print("   ✅ User login")
    print("   ✅ JWT token authentication")
    print("   ✅ Customer profile creation")
    print("\n🌐 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
