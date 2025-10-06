#!/usr/bin/env python3
"""
Analyze and test admin submission tracking to understand why submissions aren't reflecting in admin panel.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SurveyResponse, User, CustomerProfile
from app.surveys.scoring import SurveyScorer
import json

def analyze_admin_submission_tracking():
    """Analyze what submissions the admin panel captures and why they might not be showing."""
    
    print("🔍 ANALYZING ADMIN SUBMISSION TRACKING")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Check what's in the database
        print("\n1. 📊 Database Analysis")
        print("-" * 40)
        
        # Count total survey responses
        total_responses = db.query(SurveyResponse).count()
        print(f"Total SurveyResponse records: {total_responses}")
        
        # Count authenticated user responses
        auth_responses = db.query(SurveyResponse).filter(SurveyResponse.user_id.isnot(None)).count()
        print(f"Authenticated user responses: {auth_responses}")
        
        # Count guest responses (user_id is None or 0)
        guest_responses = db.query(SurveyResponse).filter(
            (SurveyResponse.user_id.is_(None)) | (SurveyResponse.user_id == 0)
        ).count()
        print(f"Guest responses: {guest_responses}")
        
        # Count users
        total_users = db.query(User).count()
        print(f"Total User records: {total_users}")
        
        # Count customer profiles
        total_profiles = db.query(CustomerProfile).count()
        print(f"Total CustomerProfile records: {total_profiles}")
        
        # 2. Analyze recent submissions
        print("\n2. 📋 Recent Submissions Analysis")
        print("-" * 40)
        
        recent_responses = db.query(SurveyResponse).order_by(SurveyResponse.created_at.desc()).limit(10).all()
        
        if recent_responses:
            print("Recent 10 submissions:")
            for i, response in enumerate(recent_responses, 1):
                print(f"  {i}. ID: {response.id}")
                print(f"     User ID: {response.user_id}")
                print(f"     Score: {response.overall_score}")
                print(f"     Created: {response.created_at}")
                print(f"     Responses: {len(response.responses) if response.responses else 0} questions")
                print()
        else:
            print("❌ No survey responses found in database!")
        
        # 3. Test guest submission flow
        print("\n3. 🧪 Testing Guest Submission Flow")
        print("-" * 40)
        
        test_responses = {
            'q1_income_stability': 3,
            'q2_income_sources': 4,
            'q3_living_expenses': 2,
            'q4_budget_tracking': 3,
            'q5_spending_control': 4,
            'q6_expense_review': 3,
            'q7_savings_rate': 2,
            'q8_emergency_fund': 3,
            'q9_savings_optimization': 4,
            'q10_payment_history': 5,
            'q11_debt_ratio': 3,
            'q12_credit_score': 4,
            'q13_retirement_planning': 2,
            'q14_insurance_coverage': 3,
            'q15_financial_planning': 4
        }
        
        # Calculate scores
        scorer = SurveyScorer()
        scores_v2 = scorer.calculate_scores_v2(test_responses, profile=None)
        scores = scorer.calculate_scores(test_responses)
        
        print(f"Test calculation successful:")
        print(f"  Total score: {scores_v2['total_score']}")
        print(f"  Pillar scores: {len(scores_v2['pillar_scores'])}")
        
        # Create a test survey response record
        try:
            new_response = SurveyResponse(
                user_id=None,  # Guest submission
                customer_profile_id=None,
                responses=test_responses,
                overall_score=scores['overall_score'],
                budgeting_score=scores['budgeting_score'],
                savings_score=scores['savings_score'],
                debt_management_score=scores['debt_management_score'],
                financial_planning_score=scores['financial_planning_score'],
                investment_knowledge_score=scores['investment_knowledge_score'],
                risk_tolerance='moderate',
                financial_goals=['emergency_fund', 'retirement'],
                completion_time=None,
                survey_version='1.0'
            )
            
            db.add(new_response)
            db.commit()
            
            print(f"✅ Test guest submission created with ID: {new_response.id}")
            
        except Exception as e:
            print(f"❌ Failed to create test submission: {e}")
            db.rollback()
        
        # 4. Check what admin panel queries
        print("\n4. 🔍 Admin Panel Query Analysis")
        print("-" * 40)
        
        # Check if admin panel looks for specific user types
        print("Checking different query patterns admin might use:")
        
        # All responses
        all_count = db.query(SurveyResponse).count()
        print(f"  All responses: {all_count}")
        
        # Only authenticated users
        auth_only = db.query(SurveyResponse).filter(SurveyResponse.user_id.isnot(None), SurveyResponse.user_id != 0).count()
        print(f"  Authenticated only: {auth_only}")
        
        # Responses with profiles
        with_profiles = db.query(SurveyResponse).filter(SurveyResponse.customer_profile_id.isnot(None)).count()
        print(f"  With customer profiles: {with_profiles}")
        
        # Recent responses (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_count = db.query(SurveyResponse).filter(SurveyResponse.created_at >= thirty_days_ago).count()
        print(f"  Recent (30 days): {recent_count}")
        
        # 5. Identify the issue
        print("\n5. 🎯 Issue Identification")
        print("-" * 40)
        
        if total_responses == 0:
            print("❌ ISSUE: No survey responses in database at all")
            print("   - Survey submissions are not being saved to database")
            print("   - Check survey submission endpoints")
        elif guest_responses == 0 and auth_responses > 0:
            print("❌ ISSUE: Only authenticated submissions, no guest submissions")
            print("   - Guest submission endpoint might not be working")
            print("   - Check /surveys/submit-guest endpoint")
        elif auth_responses == 0 and guest_responses > 0:
            print("⚠️  ISSUE: Only guest submissions, no authenticated submissions")
            print("   - Admin panel might only show authenticated user submissions")
            print("   - Check admin panel query filters")
        elif total_responses > 0:
            print("✅ Submissions exist in database")
            print("   - Issue might be in admin panel display logic")
            print("   - Check admin panel components and API endpoints")
        
        return {
            'total_responses': total_responses,
            'auth_responses': auth_responses,
            'guest_responses': guest_responses,
            'recent_responses': len(recent_responses)
        }
        
    finally:
        db.close()

def check_admin_endpoints():
    """Check what endpoints the admin panel uses to fetch submissions."""
    
    print("\n" + "=" * 60)
    print("🔍 CHECKING ADMIN ENDPOINTS")
    print("=" * 60)
    
    # Check admin routes
    admin_routes_path = os.path.join(os.path.dirname(__file__), 'app', 'admin')
    
    if os.path.exists(admin_routes_path):
        print("\n1. 📁 Admin Routes Analysis")
        print("-" * 40)
        
        # List admin route files
        for file in os.listdir(admin_routes_path):
            if file.endswith('.py') and file != '__init__.py':
                print(f"  Found admin route file: {file}")
                
                file_path = os.path.join(admin_routes_path, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Look for survey-related endpoints
                    if 'survey' in content.lower() or 'response' in content.lower():
                        print(f"    - {file} contains survey/response related code")
                    
                    # Look for specific endpoints
                    if '/submissions' in content or '/responses' in content:
                        print(f"    - {file} has submission/response endpoints")
    
    # Check frontend admin components
    frontend_admin_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'components', 'admin')
    
    if os.path.exists(frontend_admin_path):
        print("\n2. 🖥️  Frontend Admin Components")
        print("-" * 40)
        
        for file in os.listdir(frontend_admin_path):
            if file.endswith('.tsx'):
                print(f"  Found admin component: {file}")
                
                file_path = os.path.join(frontend_admin_path, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Look for API calls
                    if 'api' in content.lower() and ('survey' in content.lower() or 'submission' in content.lower()):
                        print(f"    - {file} makes survey/submission API calls")

def test_submission_endpoints():
    """Test the actual submission endpoints to see if they save to database."""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING SUBMISSION ENDPOINTS")
    print("=" * 60)
    
    import requests
    import json
    
    base_url = "http://localhost:8000"  # Adjust if different
    
    # Test guest submission
    print("\n1. 🔄 Testing Guest Submission Endpoint")
    print("-" * 40)
    
    test_data = {
        "responses": {
            "q1_income_stability": 3,
            "q2_income_sources": 4,
            "q3_living_expenses": 2,
            "q4_budget_tracking": 3,
            "q5_spending_control": 4
        },
        "completion_time": None
    }
    
    try:
        response = requests.post(f"{base_url}/surveys/submit-guest", json=test_data)
        print(f"Guest submission status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Guest submission successful")
            print(f"   Survey ID: {result.get('survey_response', {}).get('id')}")
            print(f"   Score: {result.get('score_breakdown', {}).get('overall_score')}")
        else:
            print(f"❌ Guest submission failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing guest endpoint: {e}")
    
    # Test score preview (this shouldn't save to database)
    print("\n2. 🔄 Testing Score Preview Endpoint")
    print("-" * 40)
    
    preview_data = {
        "responses": {
            "q1_income_stability": 3,
            "q2_income_sources": 4,
            "q3_living_expenses": 2
        },
        "profile": None
    }
    
    try:
        response = requests.post(f"{base_url}/surveys/calculate-preview", json=preview_data)
        print(f"Score preview status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Score preview successful")
            print(f"   Total score: {result.get('total_score')}")
            print(f"   Pillar scores: {len(result.get('pillar_scores', []))}")
        else:
            print(f"❌ Score preview failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing preview endpoint: {e}")

if __name__ == "__main__":
    print("Starting admin submission tracking analysis...")
    
    try:
        # Analyze database and submissions
        db_stats = analyze_admin_submission_tracking()
        
        # Check admin endpoints
        check_admin_endpoints()
        
        # Test endpoints
        test_submission_endpoints()
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY AND RECOMMENDATIONS")
        print("=" * 60)
        
        if db_stats['total_responses'] == 0:
            print("\n❌ CRITICAL ISSUE: No submissions in database")
            print("Recommendations:")
            print("1. Check if backend server is running")
            print("2. Verify survey submission endpoints are working")
            print("3. Check database connection and migrations")
            print("4. Test frontend submission flow")
            
        elif db_stats['guest_responses'] > 0 and db_stats['auth_responses'] == 0:
            print("\n⚠️  ISSUE: Only guest submissions, admin might filter these out")
            print("Recommendations:")
            print("1. Check if admin panel only shows authenticated user submissions")
            print("2. Modify admin queries to include guest submissions")
            print("3. Add filter options in admin panel")
            
        elif db_stats['total_responses'] > 0:
            print("\n✅ Submissions exist in database")
            print("Recommendations:")
            print("1. Check admin panel API endpoints")
            print("2. Verify admin panel query filters")
            print("3. Check admin component data fetching")
            print("4. Test admin authentication")
        
        print(f"\nDatabase Stats:")
        print(f"- Total responses: {db_stats['total_responses']}")
        print(f"- Authenticated: {db_stats['auth_responses']}")
        print(f"- Guest: {db_stats['guest_responses']}")
        print(f"- Recent: {db_stats['recent_responses']}")
        
    except Exception as e:
        print(f"\n💥 ANALYSIS ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)