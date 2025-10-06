#!/usr/bin/env python3
"""
Test admin localization endpoints to debug why admin management isn't showing anything
"""

import requests
import json

def test_admin_endpoints():
    """Test admin localization endpoints"""
    print("🔍 Testing Admin Localization Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # First, login to get admin token
    print("1. Logging in as admin...")
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"email": "admin@nationalbonds.ae", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Set up headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test admin endpoints
    endpoints = [
        "/api/admin/localized-content",
        "/api/admin/localized-content/analytics/overview",
        "/api/admin/translation-workflows",
        "/api/admin/localization/content",  # Alternative endpoint
        "/api/localization/content"  # Public endpoint for comparison
    ]
    
    print("\n2. Testing admin endpoints...")
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint}")
            
            if "localization/content" in endpoint and "admin" in endpoint:
                # This might not exist, expect 404
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            else:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'content' in data:
                            print(f"   ✅ Success: {len(data['content'])} items")
                        elif 'workflows' in data:
                            print(f"   ✅ Success: {len(data['workflows'])} workflows")
                        else:
                            print(f"   ✅ Success: {len(data)} keys in response")
                    elif isinstance(data, list):
                        print(f"   ✅ Success: {len(data)} items")
                    else:
                        print(f"   ✅ Success: {type(data)} response")
                except:
                    print(f"   ✅ Success: Non-JSON response")
            elif response.status_code == 404:
                print(f"   ⚠️  Not Found: Endpoint doesn't exist")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden: Authentication issue")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Test creating content
    print(f"\n3. Testing content creation...")
    try:
        create_data = {
            "content_type": "ui",
            "content_id": "test_admin_content",
            "language": "en",
            "text": "Test content from admin API",
            "version": "1.0"
        }
        
        response = requests.post(
            f"{base_url}/api/admin/localized-content",
            json=create_data,
            headers=headers
        )
        
        print(f"   Create Status: {response.status_code}")
        if response.status_code == 201 or response.status_code == 200:
            print("   ✅ Content creation successful")
        else:
            print(f"   ❌ Creation failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Creation error: {e}")
    
    # Test with query parameters
    print(f"\n4. Testing with filters...")
    try:
        response = requests.get(
            f"{base_url}/api/admin/localized-content?content_type=ui&language=ar&page=1&limit=10",
            headers=headers
        )
        
        print(f"   Filtered Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Filtered results: {data.get('total', 0)} total items")
        else:
            print(f"   ❌ Filter failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Filter error: {e}")

def test_frontend_expectations():
    """Test what the frontend expects vs what backend provides"""
    print(f"\n🎯 Testing Frontend Expectations")
    print("=" * 60)
    
    # The frontend expects these endpoints to work
    expected_endpoints = [
        "/api/admin/localized-content",
        "/api/admin/localized-content/analytics/overview", 
        "/api/admin/translation-workflows"
    ]
    
    print("Frontend expects these endpoints to return data:")
    for endpoint in expected_endpoints:
        print(f"  - {endpoint}")
    
    print(f"\nBackend should return:")
    print("  - /api/admin/localized-content: List of translations with pagination")
    print("  - /analytics/overview: Analytics data with counts and coverage")
    print("  - /translation-workflows: List of translation workflows")

if __name__ == "__main__":
    test_admin_endpoints()
    test_frontend_expectations()