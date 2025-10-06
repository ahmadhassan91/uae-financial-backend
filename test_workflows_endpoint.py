#!/usr/bin/env python3
"""Test workflows endpoint"""

import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "admin@nationalbonds.ae", "password": "admin123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test workflows endpoint
    response = requests.get("http://localhost:8000/api/admin/simple/translation-workflows", headers=headers)
    print(f"Workflows Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Workflows: {len(data.get('workflows', []))} workflows")
    else:
        print(f"❌ Error: {response.text}")
else:
    print("❌ Login failed")