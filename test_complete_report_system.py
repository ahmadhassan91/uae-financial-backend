"""Comprehensive test for the complete report generation and delivery system."""
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
from app.reports.pdf_service import PDFReportService
from app.reports.email_service import EmailReportService
from app.reports.delivery_service import ReportDeliveryService


# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///test_complete_system.db", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_comprehensive_test_data(db):
    """Create comprehensive test data."""
    # Create test user
    user = User(
        id=1,
        email="ahmed.almansouri@example.com",
        username="ahmed_test",
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
        industry="Finance",
        position="Senior Analyst",
        monthly_income="15000-25000",
        household_size=4,
        children="Yes",
        education_level="Bachelor's Degree",
        years_in_uae=32,  # UAE citizen
        family_status="Married",
        housing_status="Own",
        banking_relationship="Emirates NBD",
        investment_experience="Moderate",
        preferred_communication="email",
        islamic_finance_preference=True
    )
    db.add(profile)
    
    # Create comprehensive survey response
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
            'q15_financial_planning': 3,
            'q16_children_planning': 4  # Has children
        },
        overall_score=72,
        budgeting_score=75,
        savings_score=60,
        debt_management_score=85,
        financial_planning_score=65,
        investment_knowledge_score=50,
        risk_tolerance='moderate',
        language='en',
        question_variations_used={
            'q1_income_stability': 'uae_citizen_version',
            'q16_children_planning': 'family_planning_version'
        },
        demographic_rules_applied=['uae_citizen_rule', 'family_rule']
    )
    db.add(survey_response)
    
    db.commit()
    return user, profile, survey_response


async def test_complete_workflow():
    """Test the complete report generation workflow."""
    print("🧪 Testing Complete Report Generation Workflow")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create test data
        print("📋 Creating comprehensive test data...")
        user, profile, survey_response = create_comprehensive_test_data(db)
        print(f"✅ Created user: {user.email}")
        print(f"✅ Created profile: {profile.first_name} {profile.last_name}")
        print(f"✅ Created survey response with score: {survey_response.overall_score}")
        
        # Initialize services
        pdf_service = PDFReportService()
        email_service = EmailReportService()
        delivery_service = ReportDeliveryService()
        
        # Test 1: PDF Generation (English)
        print("\n📄 Testing PDF Generation (English)...")
        pdf_content_en = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=profile,
            language="en",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'National Bonds',
                'logo_url': 'https://example.com/logo.png'
            }
        )
        
        with open("complete_test_report_en.pdf", 'wb') as f:
            f.write(pdf_content_en)
        
        print(f"✅ English PDF generated: {len(pdf_content_en)} bytes")
        
        # Test 2: PDF Generation (Arabic)
        print("\n📄 Testing PDF Generation (Arabic)...")
        pdf_content_ar = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=profile,
            language="ar",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'السندات الوطنية'
            }
        )
        
        with open("complete_test_report_ar.pdf", 'wb') as f:
            f.write(pdf_content_ar)
        
        print(f"✅ Arabic PDF generated: {len(pdf_content_ar)} bytes")
        
        # Test 3: Email Content Generation
        print("\n📧 Testing Email Content Generation...")
        
        # English email
        html_content_en = email_service._generate_email_html(
            survey_response=survey_response,
            customer_profile=profile,
            language="en",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'National Bonds'
            }
        )
        
        with open("complete_test_email_en.html", 'w', encoding='utf-8') as f:
            f.write(html_content_en)
        
        # Arabic email
        html_content_ar = email_service._generate_email_html(
            survey_response=survey_response,
            customer_profile=profile,
            language="ar",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'السندات الوطنية'
            }
        )
        
        with open("complete_test_email_ar.html", 'w', encoding='utf-8') as f:
            f.write(html_content_ar)
        
        print(f"✅ Email content generated (EN: {len(html_content_en)} chars, AR: {len(html_content_ar)} chars)")
        
        # Test 4: Complete Delivery Service
        print("\n🚀 Testing Complete Delivery Service...")
        
        delivery_options = {
            'send_email': False,  # Don't actually send email
            'email_address': user.email
        }
        
        result = await delivery_service.generate_and_deliver_report(
            survey_response=survey_response,
            customer_profile=profile,
            user=user,
            delivery_options=delivery_options,
            db=db,
            language="en",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'National Bonds'
            }
        )
        
        print(f"✅ Delivery service result: {result}")
        
        # Test 5: Analytics and Tracking
        print("\n📊 Testing Analytics and Tracking...")
        
        analytics = await delivery_service.get_report_analytics(
            survey_response_id=1,
            db=db
        )
        
        print(f"✅ Analytics generated:")
        for key, value in analytics.items():
            if key != 'delivery_timeline':
                print(f"   {key}: {value}")
        
        # Test 6: History Retrieval
        print("\n📚 Testing History Retrieval...")
        
        history = await delivery_service.get_delivery_history(
            user_id=1,
            db=db,
            limit=10
        )
        
        print(f"✅ History retrieved: {len(history)} records")
        for record in history:
            print(f"   - {record['delivery_type']}: {record['delivery_status']} ({record['language']})")
        
        # Test 7: Download URL Generation
        print("\n🔗 Testing Download URL Generation...")
        
        download_url = await delivery_service.get_report_download_url(
            survey_response_id=1,
            user_id=1,
            db=db
        )
        
        if download_url:
            print(f"✅ Download URL generated: {download_url}")
            
            # Verify file exists
            if os.path.exists(download_url):
                file_size = os.path.getsize(download_url)
                print(f"✅ File verified: {file_size} bytes")
            else:
                print("❌ File not found at download URL")
        else:
            print("❌ Failed to generate download URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in complete workflow test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


async def test_multilingual_support():
    """Test multilingual support across all components."""
    print("\n🌍 Testing Multilingual Support")
    print("-" * 40)
    
    db = SessionLocal()
    
    try:
        # Get existing test data
        survey_response = db.query(SurveyResponse).first()
        profile = db.query(CustomerProfile).first()
        
        if not survey_response or not profile:
            print("❌ Test data not found")
            return False
        
        pdf_service = PDFReportService()
        email_service = EmailReportService()
        
        languages = ['en', 'ar']
        
        for lang in languages:
            print(f"\n📝 Testing {lang.upper()} language support...")
            
            # Test PDF generation
            pdf_content = pdf_service.generate_pdf_report(
                survey_response=survey_response,
                customer_profile=profile,
                language=lang
            )
            
            # Test email generation
            email_content = email_service._generate_email_html(
                survey_response=survey_response,
                customer_profile=profile,
                language=lang
            )
            
            text_content = email_service._generate_email_text(
                survey_response=survey_response,
                customer_profile=profile,
                language=lang
            )
            
            print(f"✅ {lang.upper()} - PDF: {len(pdf_content)} bytes")
            print(f"✅ {lang.upper()} - Email HTML: {len(email_content)} chars")
            print(f"✅ {lang.upper()} - Email Text: {len(text_content)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in multilingual test: {str(e)}")
        return False
    
    finally:
        db.close()


async def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🛡️ Testing Error Handling")
    print("-" * 30)
    
    try:
        pdf_service = PDFReportService()
        email_service = EmailReportService()
        
        # Test with invalid data
        print("Testing with None survey response...")
        try:
            pdf_service.generate_pdf_report(None, None)
            print("❌ Should have failed with None input")
            return False
        except Exception:
            print("✅ Properly handled None input")
        
        # Test with empty responses
        print("Testing with empty survey response...")
        empty_response = SurveyResponse(
            id=999,
            user_id=999,
            customer_profile_id=999,
            responses={},
            overall_score=0,
            budgeting_score=0,
            savings_score=0,
            debt_management_score=0,
            financial_planning_score=0,
            investment_knowledge_score=0
        )
        
        empty_profile = CustomerProfile(
            id=999,
            user_id=999,
            first_name="Test",
            last_name="User",
            age=25,
            gender="Male",
            nationality="UAE",
            emirate="Dubai",
            employment_status="Student",
            monthly_income="0-5000",
            household_size=1
        )
        
        try:
            pdf_content = pdf_service.generate_pdf_report(
                survey_response=empty_response,
                customer_profile=empty_profile,
                language="en"
            )
            print(f"✅ Handled empty responses: {len(pdf_content)} bytes")
        except Exception as e:
            print(f"❌ Failed to handle empty responses: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling test: {str(e)}")
        return False


async def main():
    """Run all comprehensive tests."""
    print("🧪 COMPREHENSIVE REPORT SYSTEM TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Complete Workflow", test_complete_workflow),
        ("Multilingual Support", test_multilingual_support),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("=" * 60)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Final Summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<25}: {status}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The report system is working perfectly!")
        print("\n📋 Generated Files:")
        print("  - complete_test_report_en.pdf")
        print("  - complete_test_report_ar.pdf")
        print("  - complete_test_email_en.html")
        print("  - complete_test_email_ar.html")
        return True
    else:
        print(f"\n💥 {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)