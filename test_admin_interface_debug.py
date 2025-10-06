#!/usr/bin/env python3
"""
Debug admin interface issues
"""

import requests
import json

def test_admin_interface():
    """Test what the admin interface is actually receiving"""
    print("🔍 Testing Admin Interface Data Flow")
    print("=" * 60)
    
    # Login
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"email": "admin@nationalbonds.ae", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test each endpoint the frontend calls
    endpoints = [
        "/api/admin/simple/localized-content",
        "/api/admin/simple/analytics", 
        "/api/admin/simple/translation-workflows"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response received")
                
                # Check specific data structure
                if endpoint.endswith('/analytics'):
                    print(f"   📊 Analytics structure:")
                    print(f"      - total_content_items: {data.get('total_content_items', 'MISSING')}")
                    print(f"      - translated_items: {data.get('translated_items', 'MISSING')}")
                    print(f"      - quality_scores: {data.get('quality_scores', 'MISSING')}")
                    print(f"      - translation_coverage: {data.get('translation_coverage', 'MISSING')}")
                    print(f"      - most_requested_content: {data.get('most_requested_content', 'MISSING')}")
                    
                elif endpoint.endswith('/localized-content'):
                    print(f"   📝 Content structure:")
                    print(f"      - content array: {len(data.get('content', []))} items")
                    print(f"      - total: {data.get('total', 'MISSING')}")
                    if data.get('content'):
                        first_item = data['content'][0]
                        print(f"      - first item keys: {list(first_item.keys())}")
                        
                elif endpoint.endswith('/translation-workflows'):
                    print(f"   🔄 Workflows structure:")
                    print(f"      - workflows array: {len(data.get('workflows', []))} items")
                    print(f"      - total: {data.get('total', 'MISSING')}")
                    
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Test the exact analytics data structure
    print(f"\n🔍 Detailed Analytics Test:")
    try:
        response = requests.get("http://localhost:8000/api/admin/simple/analytics", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("Raw analytics data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Analytics failed: {response.status_code}")
    except Exception as e:
        print(f"Analytics error: {e}")

if __name__ == "__main__":
    test_admin_interface()