#!/usr/bin/env python3
"""
Test the simple admin endpoint
"""

import requests

def test_simple_endpoint():
    """Test the simple admin endpoint"""
    print("🔍 Testing Simple Admin Endpoint")
    print("=" * 60)
    
    # Login first
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"email": "admin@nationalbonds.ae", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test simple endpoints
    endpoints = [
        "/api/admin/simple/localized-content",
        "/api/admin/simple/analytics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            print(f"\n📡 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'content' in data:
                    print(f"   ✅ Success: {len(data['content'])} items")
                elif 'total_content_items' in data:
                    print(f"   ✅ Success: {data['total_content_items']} total items")
                else:
                    print(f"   ✅ Success: {list(data.keys())}")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()