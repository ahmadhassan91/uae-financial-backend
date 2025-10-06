#!/usr/bin/env python3
"""
Create admin user for testing company tracking functionality.
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def create_admin_user():
    """Create admin user for testing."""
    admin_data = {
        "email": "admin@nationalbonds.ae",
        "username": "nb_admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        
        if response.status_code == 201:
            print("✅ Admin user created successfully")
            return True
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print("✅ Admin user already exists")
            return True
        else:
            print(f"❌ Admin user creation failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Admin user creation error: {e}")
        return False

def test_admin_login():
    """Test admin login."""
    login_data = {
        "email": "admin@nationalbonds.ae",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin login successful")
            print(f"Token: {result['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return False

if __name__ == "__main__":
    print("=== Setting up Admin User ===")
    
    if create_admin_user():
        print("\n=== Testing Admin Login ===")
        test_admin_login()
    else:
        print("Failed to create admin user")
        sys.exit(1)