#!/usr/bin/env python3
import requests
import json

LOGIN_URL = "http://localhost:8000/api/v1/auth/login"
ANALYTICS_URL = "http://localhost:8000/api/v1/admin/simple/score-analytics-table"

credentials = {"email": "admin@nationalbonds.ae", "password": "admin123"}

print("🔐 Logging in...")
login_response = requests.post(LOGIN_URL, json=credentials)
if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    print(f"✅ Login successful!")
    
    headers = {"Authorization": f"Bearer {token}"}
    print("\n📊 Fetching score analytics table...")
    response = requests.get(ANALYTICS_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Status: {response.status_code}\n")
        print(json.dumps(data, indent=2))
        
        if "questions" in data and len(data["questions"]) > 0:
            print(f"\n✅ Found {len(data['questions'])} questions")
            for q in data["questions"][:3]:
                print(f"\n  Q: {q.get('question_text', 'Unknown')[:60]}...")
                print(f"     Category: {q.get('category', 'Unknown')}")
                print(f"     Emirati Avg: {q.get('emirati', {}).get('avg_score', 0)}")
                print(f"     Non-Emirati Avg: {q.get('non_emirati', {}).get('avg_score', 0)}")
        else:
            print("\n⚠️  No questions data returned")
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text)
else:
    print(f"❌ Login failed: {login_response.status_code}")
