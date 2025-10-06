"""Test Arabic PDF generation functionality."""
import asyncio
import sys
import os
from datetime import datetime, date

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, CustomerProfile, SurveyResponse, Recommendation
from app.reports.arabic_pdf_service import ArabicPDFReportService, ArabicBrandingConfig
from app.localization.service import LocalizationService


def create_test_data(db: Session):
    """Create test data for PDF generation."""
    
    # Create test user
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        date_of_birth=datetime(1990, 1, 1),
        is_active=True
    )
    db.add(test_user)
    db.flush()
    
    # Create test customer profile
    test_profile = CustomerProfile(
        user_id=test_user.id,
        first_name="أحمد",
        last_name="محمد",
        age=33,
        gender="Male",
        nationality="UAE",
        emirate="Dubai",
        employment_status="Employed",
        monthly_income="10000-15000",
        household_size=4,
        children="Yes",
        preferred_language="ar"
    )
    db.add(test_profile)
    db.flush()
    
    # Create test survey response
    test_responses = {
        "q1_income_stability": 4,
        "q2_income_sources": 3,
        "q3_living_expenses": 4,
        "q4_budget_tracking": 3,
        "q5_spending_control": 4,
        "q6_expense_review": 3,
        "q7_savings_rate": 3,
        "q8_emergency_fund": 2,
        "q9_savings_optimization": 3,
        "q10_payment_history": 5,
        "q11_debt_ratio": 4,
        "q12_credit_score": 3,
        "q13_retirement_planning": 2,
        "q14_insurance_coverage": 3,
        "q15_financial_planning": 2,
        "q16_children_planning": 2
    }
    
    test_survey = SurveyResponse(
        user_id=test_user.id,
        customer_profile_id=test_profile.id,
        responses=test_responses,
        overall_score=68.5,
        budgeting_score=72.0,
        savings_score=65.0,
        debt_management_score=80.0,
        financial_planning_score=55.0,
        investment_knowledge_score=60.0,
        risk_tolerance="moderate",
        language="ar"
    )
    db.add(test_survey)
    db.flush()
    
    # Create test recommendations
    recommendations = [
        Recommendation(
            survey_response_id=test_survey.id,
            category="budgeting",
            title="تحسين إدارة الميزانية",
            description="ننصحك بإنشاء ميزانية شهرية مفصلة لتتبع دخلك ونفقاتك.",
            priority=1
        ),
        Recommendation(
            survey_response_id=test_survey.id,
            category="savings",
            title="بناء صندوق الطوارئ",
            description="من المهم جداً أن يكون لديك صندوق طوارئ يغطي نفقاتك لمدة 3-6 أشهر.",
            priority=2
        ),
        Recommendation(
            survey_response_id=test_survey.id,
            category="investment",
            title="بداية الاستثمار",
            description="ابدأ رحلتك الاستثمارية بتعلم الأساسيات أولاً.",
            priority=3
        )
    ]
    
    for rec in recommendations:
        db.add(rec)
    
    db.commit()
    db.refresh(test_survey)
    
    return test_user, test_profile, test_survey


async def test_arabic_pdf_generation():
    """Test Arabic PDF generation."""
    print("Testing Arabic PDF Generation...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Create test data
        print("Creating test data...")
        test_user, test_profile, test_survey = create_test_data(db)
        
        # Create localization service
        localization_service = LocalizationService(db)
        
        # Create branding config
        branding_config = ArabicBrandingConfig(
            company_name="National Bonds Corporation",
            company_name_ar="شركة السندات الوطنية",
            primary_color="#1e3a8a",
            secondary_color="#059669",
            footer_text_ar="تم إنشاء هذا التقرير بواسطة شركة السندات الوطنية"
        )
        
        # Test English PDF generation
        print("Generating English PDF...")
        pdf_service = ArabicPDFReportService(branding_config)
        english_pdf = pdf_service.generate_pdf_report(
            test_survey, 
            test_profile, 
            language="en",
            localization_service=localization_service
        )
        
        # Save English PDF
        with open("test_report_english.pdf", "wb") as f:
            f.write(english_pdf)
        print(f"✓ English PDF generated: {len(english_pdf)} bytes")
        
        # Test Arabic PDF generation
        print("Generating Arabic PDF...")
        arabic_pdf = pdf_service.generate_pdf_report(
            test_survey, 
            test_profile, 
            language="ar",
            localization_service=localization_service
        )
        
        # Save Arabic PDF
        with open("test_report_arabic.pdf", "wb") as f:
            f.write(arabic_pdf)
        print(f"✓ Arabic PDF generated: {len(arabic_pdf)} bytes")
        
        # Test Arabic text processing
        print("Testing Arabic text processing...")
        test_arabic_text = "مرحباً بك في تقرير الصحة المالية"
        processed_text = pdf_service._process_arabic_text(test_arabic_text)
        print(f"✓ Original: {test_arabic_text}")
        print(f"✓ Processed: {processed_text}")
        
        # Test font registration
        print("Testing font registration...")
        print(f"✓ Arabic font: {pdf_service.arabic_font}")
        print(f"✓ Arabic bold font: {pdf_service.arabic_font_bold}")
        
        print("\n🎉 All Arabic PDF generation tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test data
        try:
            db.query(Recommendation).filter(
                Recommendation.survey_response_id == test_survey.id
            ).delete()
            db.query(SurveyResponse).filter(
                SurveyResponse.id == test_survey.id
            ).delete()
            db.query(CustomerProfile).filter(
                CustomerProfile.id == test_profile.id
            ).delete()
            db.query(User).filter(
                User.id == test_user.id
            ).delete()
            db.commit()
            print("✓ Cleaned up test data")
        except:
            pass
        
        db.close()


async def test_localized_recommendations():
    """Test localized recommendations retrieval."""
    print("\nTesting Localized Recommendations...")
    
    db = SessionLocal()
    
    try:
        localization_service = LocalizationService(db)
        
        # Test getting Arabic recommendations
        sample_recommendations = [
            {
                "id": "budgeting_basic",
                "category": "budgeting",
                "title": "Improve Budget Management",
                "description": "Create a detailed monthly budget to track income and expenses."
            }
        ]
        
        arabic_recs = await localization_service.get_recommendations_by_language(
            sample_recommendations, "ar"
        )
        
        print(f"✓ Retrieved {len(arabic_recs)} Arabic recommendations")
        for rec in arabic_recs:
            print(f"  - {rec.get('title', 'No title')}")
        
        # Test getting Arabic UI translations
        ui_keys = ["financial_health_score", "recommendations", "budgeting", "savings"]
        arabic_ui = await localization_service.get_ui_content_by_language(ui_keys, "ar")
        
        print(f"✓ Retrieved {len(arabic_ui)} Arabic UI translations")
        for key, value in arabic_ui.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"❌ Localization test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


async def main():
    """Run all Arabic PDF tests."""
    print("=== Arabic PDF Generation Tests ===")
    
    await test_arabic_pdf_generation()
    await test_localized_recommendations()
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(main())