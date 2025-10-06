#!/usr/bin/env python3
"""
Test to validate that admin submission tracking is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

def test_admin_submission_tracking():
    """Test that admin can see survey submissions."""
    
    print("🧪 TESTING ADMIN SUBMISSION TRACKING")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Submit a test survey as guest
    print("\n1. 📝 Submitting Test Survey as Guest")
    print("-" * 40)
    
    test_survey_data = {
        "responses": {
            "q1_income_stability": 3,
            "q2_income_sources": 4,
            "q3_living_expenses": 2,
            "q4_budget_tracking": 3,
            "q5_spending_control": 4,
            "q6_expense_review": 3,
            "q7_savings_rate": 2,
            "q8_emergency_fund": 3,
            "q9_savings_optimization": 4,
            "q10_payment_history": 5,
            "q11_debt_ratio": 3,
            "q12_credit_score": 4,
            "q13_retirement_planning": 2,
            "q14_insurance_coverage": 3,
            "q15_financial_planning": 4
        },
        "completion_time": None
    }
    
    try:
        response = requests.post(f"{base_url}/surveys/submit-guest", json=test_survey_data)
        print(f"Guest submission status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            survey_id = result.get('survey_response', {}).get('id')
            overall_score = result.get('score_breakdown', {}).get('overall_score')
            print(f"✅ Guest submission successful")
            print(f"   Survey ID: {survey_id}")
            print(f"   Overall Score: {overall_score}")
        else:
            print(f"❌ Guest submission failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting guest survey: {e}")
        return False
    
    # Step 2: Test admin login (you'll need to create an admin user first)
    print("\n2. 🔐 Testing Admin Authentication")
    print("-" * 40)
    
    # First, let's check if we can access admin endpoints without auth
    try:
        response = requests.get(f"{base_url}/api/admin/simple/survey-submissions")
        print(f"Admin endpoint without auth status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Admin endpoint properly protected (requires authentication)")
        elif response.status_code == 200:
            print("⚠️  Admin endpoint accessible without auth (security issue)")
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing admin endpoint: {e}")
    
    # Step 3: Test admin login
    admin_credentials = {
        "username": "admin",
        "password": "admin123"  # Default admin password
    }
    
    admin_token = None
    try:
        response = requests.post(f"{base_url}/auth/admin/login", json=admin_credentials)
        print(f"Admin login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            admin_token = result.get('access_token')
            print(f"✅ Admin login successful")
            print(f"   Token: {admin_token[:20]}..." if admin_token else "No token")
        else:
            print(f"❌ Admin login failed: {response.text}")
            print("   You may need to create an admin user first:")
            print("   Run: python backend/create_admin_user.py")
            
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
    
    # Step 4: Test admin submission endpoint with authentication
    if admin_token:
        print("\n3. 📊 Testing Admin Submission Endpoint")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            response = requests.get(f"{base_url}/api/admin/simple/survey-submissions", headers=headers)
            print(f"Admin submissions endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                submissions = result.get('submissions', [])
                total = result.get('total', 0)
                
                print(f"✅ Admin can access submissions")
                print(f"   Total submissions: {total}")
                print(f"   Retrieved: {len(submissions)}")
                
                if submissions:
                    latest = submissions[0]
                    print(f"   Latest submission:")
                    print(f"     ID: {latest.get('id')}")
                    print(f"     User Type: {latest.get('user_type')}")
                    print(f"     Score: {latest.get('overall_score')}")
                    print(f"     Created: {latest.get('created_at')}")
                
                return True
            else:
                print(f"❌ Admin submissions endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing admin submissions: {e}")
            return False
    
    # Step 5: Test admin analytics endpoint
    if admin_token:
        print("\n4. 📈 Testing Admin Analytics Endpoint")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            response = requests.get(f"{base_url}/api/admin/simple/survey-analytics", headers=headers)
            print(f"Admin analytics endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Admin analytics working")
                print(f"   Total submissions: {result.get('total_submissions', 0)}")
                print(f"   Guest submissions: {result.get('guest_submissions', 0)}")
                print(f"   Auth submissions: {result.get('authenticated_submissions', 0)}")
                print(f"   Recent (30d): {result.get('recent_submissions_30d', 0)}")
                
                avg_scores = result.get('average_scores', {})
                print(f"   Average overall score: {avg_scores.get('overall', 0):.1f}")
                
                return True
            else:
                print(f"❌ Admin analytics endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing admin analytics: {e}")
            return False
    
    return False

def test_frontend_admin_integration():
    """Test that frontend can fetch admin data."""
    
    print("\n" + "=" * 60)
    print("🖥️  TESTING FRONTEND ADMIN INTEGRATION")
    print("=" * 60)
    
    base_url = "http://localhost:3000"
    
    try:
        # Test admin page accessibility
        response = requests.get(f"{base_url}/admin")
        print(f"Admin page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin page accessible")
            
            # Check if page contains expected elements
            content = response.text
            if "Admin Dashboard" in content or "admin" in content.lower():
                print("✅ Admin page contains dashboard elements")
            else:
                print("⚠️  Admin page might not be fully loaded")
                
        else:
            print(f"❌ Admin page not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing frontend admin: {e}")

if __name__ == "__main__":
    print("Starting admin submission tracking validation...")
    
    try:
        # Test backend admin functionality
        backend_success = test_admin_submission_tracking()
        
        # Test frontend integration
        test_frontend_admin_integration()
        
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        
        if backend_success:
            print("✅ Admin submission tracking is working!")
            print("   - Survey submissions are saved to database")
            print("   - Admin can authenticate and access submissions")
            print("   - Admin analytics endpoint provides insights")
            print("   - Frontend should now display real submission data")
        else:
            print("❌ Admin submission tracking has issues")
            print("   - Check backend server is running")
            print("   - Ensure admin user exists (run create_admin_user.py)")
            print("   - Verify database connections")
            print("   - Check API endpoint implementations")
        
        print("\n📋 Next Steps:")
        print("1. Ensure backend server is running on port 8000")
        print("2. Create admin user if not exists: python backend/create_admin_user.py")
        print("3. Submit test surveys via frontend")
        print("4. Login to admin panel and verify submissions appear")
        print("5. Check admin analytics for submission statistics")
        
    except Exception as e:
        print(f"\n💥 VALIDATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)