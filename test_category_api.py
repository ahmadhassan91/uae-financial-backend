#!/usr/bin/env python3
"""
Test Category Performance API with Authentication
"""
import requests
import json

# Login credentials
LOGIN_URL = "http://localhost:8000/api/v1/auth/login"
CATEGORY_URL = "http://localhost:8000/api/v1/admin/simple/category-performance"

credentials = {
    "email": "admin@nationalbonds.ae",
    "password": "admin123"
}

print("🔐 Logging in...")
login_response = requests.post(LOGIN_URL, json=credentials)

if login_response.status_code == 200:
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    print(f"✅ Login successful! Token: {access_token[:20]}...")
    
    # Make authenticated request to category performance endpoint
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print("\n📊 Fetching category performance data...")
    category_response = requests.get(CATEGORY_URL, headers=headers)
    
    if category_response.status_code == 200:
        data = category_response.json()
        print(f"✅ Success! Status: {category_response.status_code}")
        print("\n📈 Category Performance Data:")
        print(json.dumps(data, indent=2))
        
        # Detailed analysis
        if "categories" in data:
            print("\n\n🔍 Detailed Category Analysis:")
            for cat in data["categories"]:
                print(f"\n  Category: {cat.get('category', 'Unknown')}")
                print(f"    - Average Score: {cat.get('avg_score', 0)}")
                print(f"    - Count: {cat.get('count', 0)}")
                print(f"    - Raw Data: {cat}")
    else:
        print(f"❌ Error {category_response.status_code}: {category_response.text}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
