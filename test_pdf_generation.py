"""Test script for PDF report generation."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.reports.pdf_service import PDFReportService, BrandingConfig
from app.models import SurveyResponse, CustomerProfile
from datetime import datetime


def test_pdf_generation():
    """Test PDF generation with mock data."""
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
    
    # Test 1: Default branding
    print("=== Test 1: Default Branding ===")
    pdf_service = PDFReportService()
    
    try:
        # Generate PDF with charts
        print("Generating PDF report with charts...")
        pdf_content = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en"
        )
        
        # Save to file
        output_file = "test_report.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 File saved as: {output_file}")
        print(f"📊 File size: {len(pdf_content)} bytes")
        
        # Test 2: Custom branding
        print("\n=== Test 2: Custom Branding ===")
        custom_branding = BrandingConfig(
            primary_color="#2563eb",  # Blue
            secondary_color="#10b981",  # Emerald
            accent_color="#f59e0b",  # Amber
            company_name="Custom Financial Services",
            website="www.customfinance.ae",
            footer_text="Custom footer text for branded reports.",
            show_charts=True,
            chart_style="modern"
        )
        
        pdf_content_custom = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en",
            branding_config=custom_branding
        )
        
        output_file_custom = "test_report_custom_branding.pdf"
        with open(output_file_custom, 'wb') as f:
            f.write(pdf_content_custom)
        
        print(f"✅ Custom branded PDF generated successfully!")
        print(f"📄 File saved as: {output_file_custom}")
        print(f"📊 File size: {len(pdf_content_custom)} bytes")
        
        # Test 3: Summary report
        print("\n=== Test 3: Summary Report ===")
        pdf_content_summary = pdf_service.generate_summary_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="en"
        )
        
        output_file_summary = "test_report_summary.pdf"
        with open(output_file_summary, 'wb') as f:
            f.write(pdf_content_summary)
        
        print(f"✅ Summary PDF generated successfully!")
        print(f"📄 File saved as: {output_file_summary}")
        print(f"📊 File size: {len(pdf_content_summary)} bytes")
        
        # Test 4: Arabic version with custom branding
        print("\n=== Test 4: Arabic with Custom Branding ===")
        pdf_content_ar = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="ar",
            branding_config=custom_branding
        )
        
        output_file_ar = "test_report_arabic.pdf"
        with open(output_file_ar, 'wb') as f:
            f.write(pdf_content_ar)
        
        print(f"✅ Arabic PDF generated successfully!")
        print(f"📄 File saved as: {output_file_ar}")
        print(f"📊 File size: {len(pdf_content_ar)} bytes")
        
        # Test 5: Branded PDF from dictionary data
        print("\n=== Test 5: Branded PDF from Dictionary ===")
        survey_dict = {
            'id': 1,
            'user_id': 1,
            'responses': {
                'q1_income_stability': 4,
                'q2_income_sources': 3,
                'q3_living_expenses': 4,
            },
            'overall_score': 75,
            'budgeting_score': 80,
            'savings_score': 70,
            'debt_management_score': 85,
            'financial_planning_score': 65,
            'investment_knowledge_score': 60,
            'risk_tolerance': 'moderate',
            'profile': {
                'first_name': 'Sara',
                'last_name': 'Ahmed',
                'age': 28,
                'nationality': 'UAE',
                'emirate': 'Abu Dhabi'
            }
        }
        
        pdf_content_dict = pdf_service.generate_branded_pdf(
            survey_data=survey_dict,
            branding_config=custom_branding,
            language="en"
        )
        
        output_file_dict = "test_report_from_dict.pdf"
        with open(output_file_dict, 'wb') as f:
            f.write(pdf_content_dict)
        
        print(f"✅ Dictionary-based PDF generated successfully!")
        print(f"📄 File saved as: {output_file_dict}")
        print(f"📊 File size: {len(pdf_content_dict)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF generation test completed successfully!")
    else:
        print("\n💥 PDF generation test failed!")
        sys.exit(1)