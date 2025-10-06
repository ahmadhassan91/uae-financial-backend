"""Test script for email service (without actually sending emails)."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.reports.email_service import EmailReportService
from app.reports.pdf_service import PDFReportService
from app.models import SurveyResponse, CustomerProfile
from datetime import datetime


def test_email_generation():
    """Test email content generation without sending."""
    # Create mock survey response
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
        risk_tolerance='moderate',
        created_at=datetime.now()
    )
    
    # Create mock customer profile
    customer_profile = CustomerProfile(
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
    
    # Initialize services
    email_service = EmailReportService()
    pdf_service = PDFReportService()
    
    try:
        # Generate PDF content for email attachment
        print("Generating PDF content for email...")
        pdf_content = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en"
        )
        
        # Test English email content generation
        print("Generating English email content...")
        html_content_en = email_service._generate_email_html(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'National Bonds',
                'logo_url': 'https://example.com/logo.png'
            }
        )
        
        # Save English email to file for inspection
        with open("test_email_en.html", 'w', encoding='utf-8') as f:
            f.write(html_content_en)
        
        print("✅ English email content generated successfully!")
        print(f"📄 Saved as: test_email_en.html")
        
        # Test Arabic email content generation
        print("Generating Arabic email content...")
        html_content_ar = email_service._generate_email_html(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="ar",
            branding_config={
                'primary_color': '#1e3a8a',
                'secondary_color': '#059669',
                'company_name': 'السندات الوطنية',
                'logo_url': 'https://example.com/logo.png'
            }
        )
        
        # Save Arabic email to file for inspection
        with open("test_email_ar.html", 'w', encoding='utf-8') as f:
            f.write(html_content_ar)
        
        print("✅ Arabic email content generated successfully!")
        print(f"📄 Saved as: test_email_ar.html")
        
        # Test plain text content
        print("Generating plain text content...")
        text_content_en = email_service._generate_email_text(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en"
        )
        
        text_content_ar = email_service._generate_email_text(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="ar"
        )
        
        print("✅ Plain text content generated successfully!")
        print(f"📝 English text length: {len(text_content_en)} characters")
        print(f"📝 Arabic text length: {len(text_content_ar)} characters")
        
        # Test reminder email content
        print("Generating reminder email content...")
        reminder_en = email_service._get_reminder_content_en("Ahmed")
        reminder_ar = email_service._get_reminder_content_ar("أحمد")
        
        with open("test_reminder_en.html", 'w', encoding='utf-8') as f:
            f.write(reminder_en)
        
        with open("test_reminder_ar.html", 'w', encoding='utf-8') as f:
            f.write(reminder_ar)
        
        print("✅ Reminder email content generated successfully!")
        print(f"📄 Saved as: test_reminder_en.html and test_reminder_ar.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating email content: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_email_service_config():
    """Test email service configuration."""
    print("Testing email service configuration...")
    
    email_service = EmailReportService()
    
    print(f"SMTP Server: {email_service.smtp_server}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"From Email: {email_service.from_email}")
    print(f"From Name: {email_service.from_name}")
    print(f"Jinja Environment: {'Available' if email_service.jinja_env else 'Not Available'}")
    
    return True


if __name__ == "__main__":
    print("🧪 Testing Email Service...")
    print("=" * 50)
    
    config_success = test_email_service_config()
    print()
    
    generation_success = test_email_generation()
    
    if config_success and generation_success:
        print("\n🎉 Email service tests completed successfully!")
        print("\n📋 Generated files:")
        print("  - test_email_en.html (English email)")
        print("  - test_email_ar.html (Arabic email)")
        print("  - test_reminder_en.html (English reminder)")
        print("  - test_reminder_ar.html (Arabic reminder)")
        print("\n💡 Note: No actual emails were sent during testing.")
    else:
        print("\n💥 Email service tests failed!")
        sys.exit(1)