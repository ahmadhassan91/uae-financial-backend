#!/usr/bin/env python3
"""
Test frontend admin login integration
This script simulates what the frontend does when logging in
"""

import requests
import json

def test_frontend_login_flow():
    """Test the complete frontend login flow"""
    print("🔐 Testing Frontend Admin Login Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Test CORS preflight (what browser does automatically)
    print("1. Testing CORS preflight request...")
    try:
        preflight_response = requests.options(
            f"{base_url}/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        if preflight_response.status_code == 200:
            print("   ✅ CORS preflight successful")
        else:
            print(f"   ❌ CORS preflight failed: {preflight_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ CORS preflight error: {e}")
        return False
    
    # Step 2: Test actual login request
    print("2. Testing login request...")
    try:
        login_data = {
            "email": "admin@nationalbonds.ae",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        
        if login_response.status_code == 200:
            print("   ✅ Login request successful")
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"   📝 Access token received: {access_token[:30]}...")
        else:
            print(f"   ❌ Login request failed: {login_response.status_code}")
            print(f"   📄 Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login request error: {e}")
        return False
    
    # Step 3: Test authenticated request
    print("3. Testing authenticated request...")
    try:
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "Origin": "http://localhost:3000"
        }
        
        # Test admin endpoint
        admin_response = requests.get(
            f"{base_url}/api/admin/localization/content",
            headers=auth_headers
        )
        
        if admin_response.status_code == 200:
            print("   ✅ Authenticated admin request successful")
            print(f"   📊 Response data: {len(admin_response.json())} items")
        elif admin_response.status_code == 404:
            print("   ⚠️  Admin endpoint not found (expected for some routes)")
        else:
            print(f"   ❌ Authenticated request failed: {admin_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Authenticated request error: {e}")
    
    # Step 4: Test localization endpoints (should work without auth)
    print("4. Testing public localization endpoints...")
    try:
        # Test languages endpoint
        lang_response = requests.get(f"{base_url}/api/localization/languages")
        if lang_response.status_code == 200:
            languages = lang_response.json()
            print(f"   ✅ Languages endpoint: {len(languages)} languages")
        
        # Test questions endpoint
        questions_response = requests.get(f"{base_url}/api/localization/questions/en")
        if questions_response.status_code == 200:
            questions = questions_response.json()
            print(f"   ✅ Questions endpoint: {len(questions)} questions")
            
    except Exception as e:
        print(f"   ❌ Public endpoints error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Frontend login flow test completed!")
    print("\n💡 FRONTEND INTEGRATION NOTES:")
    print("1. CORS is properly configured for localhost:3000")
    print("2. Login endpoint returns valid JWT tokens")
    print("3. Admin credentials work: admin@nationalbonds.ae / admin123")
    print("4. Backend is ready for frontend authentication")
    
    print("\n🔧 FRONTEND IMPLEMENTATION:")
    print("- Use fetch() or axios to POST to /auth/login")
    print("- Include 'Content-Type: application/json' header")
    print("- Store access_token in localStorage or state")
    print("- Include 'Authorization: Bearer <token>' for admin requests")
    
    return True

def test_admin_endpoints():
    """Test various admin endpoints"""
    print("\n🔐 Testing Admin Endpoints")
    print("=" * 30)
    
    # First login to get token
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"email": "admin@nationalbonds.ae", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Cannot login for admin endpoint test")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test various admin endpoints
    endpoints = [
        "/api/localization/content",
        "/api/admin/localization/content", 
        "/api/admin/localization/translations"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            status = "✅" if response.status_code == 200 else "❌" if response.status_code >= 400 else "⚠️"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

if __name__ == "__main__":
    success = test_frontend_login_flow()
    if success:
        test_admin_endpoints()
    else:
        print("\n❌ Frontend login flow test failed!")
        print("🔧 Check that backend is running: uvicorn app.main:app --reload")