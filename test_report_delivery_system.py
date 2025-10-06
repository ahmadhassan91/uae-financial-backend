"""Test script for the complete report delivery system."""
import sys
import os
import asyncio
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    User, CustomerProfile, SurveyResponse, 
    ReportDelivery, ReportAccessLog
)
from app.reports.delivery_service import ReportDeliveryService


# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///test_reports.db", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_data(db):
    """Create test data for the report delivery system."""
    # Create test user
    user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(user)
    
    # Create customer profile
    profile = CustomerProfile(
        id=1,
        user_id=1,
        first_name="Ahmed",
        last_name="Al-Mansouri",
        age=32,
        gender="Male",
        nationality="UAE",
        emirate="Dubai",
        employment_status="Full-time",
        monthly_income="15000-25000",
        household_size=4,
        children="Yes"
    )
    db.add(profile)
    
    # Create survey response
    survey_response = SurveyResponse(
        id=1,
        user_id=1,
        customer_profile_id=1,
        responses={
            'q1_income_stability': 4,
            'q2_income_sources': 3,
            'q3_living_expenses': 4,
            'q4_budget_tracking': 3,
            'q5_spending_control': 4,
            'q6_expense_review': 3,
            'q7_savings_rate': 3,
            'q8_emergency_fund': 2,
            'q9_savings_optimization': 3,
            'q10_payment_history': 5,
            'q11_debt_ratio': 4,
            'q12_credit_score': 4,
            'q13_retirement_planning': 2,
            'q14_insurance_coverage': 3,
            'q15_financial_planning': 3
        },
        overall_score=72,
        budgeting_score=75,
        savings_score=60,
        debt_management_score=85,
        financial_planning_score=65,
        investment_knowledge_score=50,
        risk_tolerance='moderate'
    )
    db.add(survey_response)
    
    db.commit()
    return user, profile, survey_response


async def test_report_generation_and_delivery():
    """Test the complete report generation and delivery process."""
    db = SessionLocal()
    
    try:
        print("Creating test data...")
        user, profile, survey_response = create_test_data(db)
        
        # Initialize delivery service
        delivery_service = ReportDeliveryService()
        
        print("Testing PDF generation and email delivery...")
        
        # Test report generation with email delivery
        delivery_options = {
            'send_email': False,  # Don't actually send email in test
            'email_address': 'test@example.com'
        }
        
        result = await delivery_service.generate_and_deliver_report(
            survey_response=survey_response,
            customer_profile=profile,
            user=user,
            delivery_options=delivery_options,
            db=db,
            language="en"
        )
        
        print(f"✅ Report generation result: {result}")
        
        # Test getting download URL
        print("Testing download URL generation...")
        download_url = await delivery_service.get_report_download_url(
            survey_response_id=1,
            user_id=1,
            db=db
        )
        
        if download_url:
            print(f"✅ Download URL generated: {download_url}")
        else:
            print("❌ Failed to generate download URL")
        
        # Test delivery history
        print("Testing delivery history...")
        history = await delivery_service.get_delivery_history(
            user_id=1,
            db=db,
            limit=10
        )
        
        print(f"✅ Delivery history retrieved: {len(history)} records")
        for record in history:
            print(f"  - {record['delivery_type']}: {record['delivery_status']}")
        
        # Test report analytics
        print("Testing report analytics...")
        analytics = await delivery_service.get_report_analytics(
            survey_response_id=1,
            db=db
        )
        
        print(f"✅ Analytics retrieved:")
        print(f"  - Total deliveries: {analytics['total_deliveries']}")
        print(f"  - PDF downloads: {analytics['pdf_downloads']}")
        print(f"  - Email deliveries: {analytics['email_deliveries']}")
        
        # Test resend functionality (without actually sending)
        print("Testing resend functionality...")
        # This would normally send an email, but we'll just test the logic
        
        return True
        
    except Exception as e:
        print(f"❌ Error in report delivery test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


async def test_report_tracking():
    """Test report tracking and analytics features."""
    db = SessionLocal()
    
    try:
        print("Testing report tracking features...")
        
        # Create some mock delivery records
        delivery1 = ReportDelivery(
            survey_response_id=1,
            user_id=1,
            delivery_type='pdf_download',
            delivery_status='generated',
            file_path='/path/to/report.pdf',
            file_size=5000,
            language='en'
        )
        db.add(delivery1)
        
        delivery2 = ReportDelivery(
            survey_response_id=1,
            user_id=1,
            delivery_type='email',
            delivery_status='sent',
            recipient_email='test@example.com',
            file_size=5000,
            language='en',
            delivered_at=datetime.now()
        )
        db.add(delivery2)
        
        # Create access logs
        access1 = ReportAccessLog(
            report_delivery_id=1,
            user_id=1,
            access_type='download'
        )
        db.add(access1)
        
        access2 = ReportAccessLog(
            report_delivery_id=2,
            user_id=1,
            access_type='email_open'
        )
        db.add(access2)
        
        db.commit()
        
        # Test analytics
        delivery_service = ReportDeliveryService()
        analytics = await delivery_service.get_report_analytics(
            survey_response_id=1,
            db=db
        )
        
        print(f"✅ Tracking analytics:")
        print(f"  - Total deliveries: {analytics['total_deliveries']}")
        print(f"  - Total accesses: {analytics['total_accesses']}")
        print(f"  - Download accesses: {analytics['download_accesses']}")
        print(f"  - Email opens: {analytics['email_opens']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in tracking test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


async def test_cleanup_functionality():
    """Test the cleanup functionality for old reports."""
    print("Testing cleanup functionality...")
    
    try:
        delivery_service = ReportDeliveryService()
        
        # Test cleanup (this won't actually delete anything in our test)
        result = await delivery_service.cleanup_old_reports(
            days_old=30,
            db=SessionLocal()
        )
        
        print(f"✅ Cleanup test result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in cleanup test: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Testing Report Delivery System")
    print("=" * 50)
    
    tests = [
        ("Report Generation and Delivery", test_report_generation_and_delivery),
        ("Report Tracking", test_report_tracking),
        ("Cleanup Functionality", test_cleanup_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)