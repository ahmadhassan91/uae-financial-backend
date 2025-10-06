#!/usr/bin/env python3
"""
Test script for incomplete survey tracking functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_incomplete_survey_system():
    """Test the complete incomplete survey tracking system"""
    
    print("🧪 INCOMPLETE SURVEY SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Start Guest Incomplete Survey
    print("\n1️⃣ Testing Guest Incomplete Survey Start...")
    guest_survey_data = {
        "current_step": 0,
        "total_steps": 10,
        "responses": {},
        "email": "test.incomplete@example.com",
        "phone_number": "+971501234567"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/surveys/incomplete/start-guest", json=guest_survey_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Guest incomplete survey started successfully")
            print(f"   Session ID: {result['session_id'][:20]}...")
            print(f"   Total Steps: {result['total_steps']}")
            session_id = result['session_id']
        else:
            print(f"❌ Failed to start guest survey: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Guest survey start error: {e}")
        return False
    
    # Test 2: Update Incomplete Survey Progress
    print("\n2️⃣ Testing Survey Progress Update...")
    update_data = {
        "current_step": 3,
        "responses": {
            "Q1": 4,
            "Q2": 3,
            "Q3": 5
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/surveys/incomplete/{session_id}", json=update_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Survey progress updated successfully")
            print(f"   Current Step: {result['current_step']}")
            print(f"   Responses: {len(result['responses'])} questions answered")
        else:
            print(f"❌ Failed to update progress: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Progress update error: {e}")
        return False
    
    # Test 3: Register User for Admin Tests
    print("\n3️⃣ Setting up Admin User...")
    admin_data = {
        "email": "admin@example.com",
        "username": "admin_user",
        "password": "adminpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 201:
            print("✅ Admin user created successfully")
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print("✅ Admin user already exists")
        else:
            print(f"❌ Admin user creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin user creation error: {e}")
        return False
    
    # Test 4: Admin Login
    print("\n4️⃣ Testing Admin Login...")
    login_data = {
        "email": "admin@example.com",
        "password": "adminpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin login successful")
            admin_token = result['access_token']
            headers = {"Authorization": f"Bearer {admin_token}"}
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return False
    
    # Test 5: Get Incomplete Survey Stats
    print("\n5️⃣ Testing Admin Stats Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/surveys/incomplete/admin/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin stats retrieved successfully")
            print(f"   Total Incomplete: {stats['total_incomplete']}")
            print(f"   Abandoned Count: {stats['abandoned_count']}")
            print(f"   Average Completion: {stats['average_completion_rate']}%")
            print(f"   Follow-up Pending: {stats['follow_up_pending']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Stats retrieval error: {e}")
        return False
    
    # Test 6: List Incomplete Surveys
    print("\n6️⃣ Testing Admin Survey List...")
    try:
        response = requests.get(f"{BASE_URL}/surveys/incomplete/admin/list", headers=headers)
        if response.status_code == 200:
            surveys = response.json()
            print("✅ Admin survey list retrieved successfully")
            print(f"   Found {len(surveys)} incomplete surveys")
            if surveys:
                survey = surveys[0]
                print(f"   Sample survey: Step {survey['current_step']}/{survey['total_steps']}")
        else:
            print(f"❌ Failed to get survey list: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Survey list error: {e}")
        return False
    
    # Test 7: Complete Survey Session
    print("\n7️⃣ Testing Survey Completion...")
    try:
        response = requests.delete(f"{BASE_URL}/surveys/incomplete/{session_id}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Survey session completed successfully")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Failed to complete session: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Session completion error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_incomplete_survey_system()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL INCOMPLETE SURVEY TESTS PASSED!")
        print("✅ Guest users can start incomplete surveys")
        print("✅ Survey progress is tracked and updated")
        print("✅ Admin can view stats and incomplete surveys")
        print("✅ Survey sessions can be completed")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    print("=" * 50)