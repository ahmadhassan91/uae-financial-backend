#!/usr/bin/env python3
"""
Simple script to check what survey submissions exist in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SurveyResponse, User, CustomerProfile

def check_database_submissions():
    """Check what survey submissions exist in the database."""
    
    print("🔍 CHECKING DATABASE SUBMISSIONS")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Count total survey responses
        total_responses = db.query(SurveyResponse).count()
        print(f"\n📊 Total SurveyResponse records: {total_responses}")
        
        if total_responses == 0:
            print("❌ No survey responses found in database!")
            print("\nPossible reasons:")
            print("1. No surveys have been submitted yet")
            print("2. Survey submission endpoints are not working")
            print("3. Database connection issues")
            print("4. Survey data is being stored elsewhere")
            return False
        
        # Count by user type
        guest_responses = db.query(SurveyResponse).filter(
            (SurveyResponse.user_id.is_(None)) | (SurveyResponse.user_id == 0)
        ).count()
        
        auth_responses = db.query(SurveyResponse).filter(
            SurveyResponse.user_id.isnot(None), SurveyResponse.user_id != 0
        ).count()
        
        print(f"👤 Guest responses: {guest_responses}")
        print(f"🔐 Authenticated responses: {auth_responses}")
        
        # Show recent submissions
        print(f"\n📋 Recent Submissions (last 10):")
        print("-" * 40)
        
        recent_responses = db.query(SurveyResponse).order_by(
            SurveyResponse.created_at.desc()
        ).limit(10).all()
        
        for i, response in enumerate(recent_responses, 1):
            user_type = "Guest" if not response.user_id else f"User {response.user_id}"
            print(f"{i:2d}. ID: {response.id:3d} | {user_type:10s} | Score: {response.overall_score:5.1f} | {response.created_at}")
        
        # Check score distribution
        print(f"\n📈 Score Distribution:")
        print("-" * 40)
        
        excellent = db.query(SurveyResponse).filter(SurveyResponse.overall_score >= 65).count()
        good = db.query(SurveyResponse).filter(
            SurveyResponse.overall_score >= 50, SurveyResponse.overall_score < 65
        ).count()
        fair = db.query(SurveyResponse).filter(
            SurveyResponse.overall_score >= 35, SurveyResponse.overall_score < 50
        ).count()
        needs_improvement = db.query(SurveyResponse).filter(SurveyResponse.overall_score < 35).count()
        
        print(f"Excellent (65+):     {excellent:3d} ({excellent/total_responses*100:5.1f}%)")
        print(f"Good (50-64):        {good:3d} ({good/total_responses*100:5.1f}%)")
        print(f"Fair (35-49):        {fair:3d} ({fair/total_responses*100:5.1f}%)")
        print(f"Needs Improvement:   {needs_improvement:3d} ({needs_improvement/total_responses*100:5.1f}%)")
        
        # Check if responses have actual data
        print(f"\n🔍 Data Quality Check:")
        print("-" * 40)
        
        responses_with_data = db.query(SurveyResponse).filter(
            SurveyResponse.responses.isnot(None)
        ).count()
        
        print(f"Responses with survey data: {responses_with_data}/{total_responses}")
        
        if responses_with_data > 0:
            # Check a sample response
            sample = db.query(SurveyResponse).filter(
                SurveyResponse.responses.isnot(None)
            ).first()
            
            if sample and sample.responses:
                question_count = len(sample.responses)
                print(f"Sample response has {question_count} questions answered")
                
                # Show first few questions
                if isinstance(sample.responses, dict):
                    questions = list(sample.responses.keys())[:5]
                    print(f"Sample questions: {', '.join(questions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

def create_test_submission():
    """Create a test submission to verify database is working."""
    
    print(f"\n🧪 Creating Test Submission")
    print("-" * 40)
    
    db = next(get_db())
    
    try:
        from app.surveys.scoring import SurveyScorer
        
        # Test responses
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
        scores = scorer.calculate_scores(test_responses)
        
        # Create test submission
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
        
        print(f"✅ Test submission created successfully!")
        print(f"   ID: {new_response.id}")
        print(f"   Overall Score: {new_response.overall_score}")
        print(f"   Questions: {len(test_responses)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test submission: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Checking database submissions...")
    
    # Check existing submissions
    has_submissions = check_database_submissions()
    
    # If no submissions, create a test one
    if not has_submissions:
        print(f"\n💡 No submissions found. Creating test submission...")
        create_test_submission()
        
        # Check again
        print(f"\n🔄 Checking database again after test submission...")
        check_database_submissions()
    
    print(f"\n✅ Database check complete!")
    print(f"\nNext steps:")
    print(f"1. If no submissions: Submit surveys via frontend")
    print(f"2. If submissions exist: Check admin panel display")
    print(f"3. Verify admin authentication is working")
    print(f"4. Test admin API endpoints")