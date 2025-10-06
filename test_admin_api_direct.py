#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

def test_admin_api():
    """Test admin API endpoints directly"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 TESTING ADMIN API ENDPOINTS")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n1. Testing admin login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            admin_token = login_result.get("access_token")
            print(f"✅ Admin login successful")
            print(f"   Token: {admin_token[:20]}...")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return
    
    # Step 2: Test survey submissions endpoint
    print("\n2. Testing survey submissions endpoint...")
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        submissions_response = requests.get(
            f"{base_url}/api/admin/simple/survey-submissions?limit=100",
            headers=headers
        )
        
        if submissions_response.status_code == 200:
            submissions_data = submissions_response.json()
            print(f"✅ Survey submissions endpoint working")
            print(f"   Total submissions: {submissions_data.get('total', 0)}")
            print(f"   Returned submissions: {len(submissions_data.get('submissions', []))}")
            
            # Show first submission details
            if submissions_data.get('submissions'):
                first_submission = submissions_data['submissions'][0]
                print(f"   First submission ID: {first_submission.get('id')}")
                print(f"   User ID: {first_submission.get('user_id')}")
                print(f"   Overall score: {first_submission.get('overall_score')}")
                print(f"   Created: {first_submission.get('created_at')}")
            
        else:
            print(f"❌ Survey submissions failed: {submissions_response.status_code}")
            print(f"   Response: {submissions_response.text}")
            
    except Exception as e:
        print(f"❌ Survey submissions error: {e}")
    
    # Step 3: Test survey analytics endpoint
    print("\n3. Testing survey analytics endpoint...")
    try:
        analytics_response = requests.get(
            f"{base_url}/api/admin/simple/survey-analytics",
            headers=headers
        )
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"✅ Survey analytics endpoint working")
            print(f"   Total submissions: {analytics_data.get('total_submissions', 0)}")
            print(f"   Guest submissions: {analytics_data.get('guest_submissions', 0)}")
            print(f"   Auth submissions: {analytics_data.get('authenticated_submissions', 0)}")
            
        else:
            print(f"❌ Survey analytics failed: {analytics_response.status_code}")
            print(f"   Response: {analytics_response.text}")
            
    except Exception as e:
        print(f"❌ Survey analytics error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Admin API test complete!")

if __name__ == "__main__":
    test_admin_api()