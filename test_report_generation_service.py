"""Test script for the ReportGenerationService."""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.reports.report_generation_service import ReportGenerationService
from app.reports.pdf_service import BrandingConfig
from app.models import SurveyResponse, CustomerProfile
from datetime import datetime


async def test_report_generation_service():
    """Test the ReportGenerationService with various scenarios."""
    
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
        first_name="Fatima",
        last_name="Al-Zahra",
        age=29,
        gender="Female",
        nationality="UAE",
        emirate="Abu Dhabi",
        employment_status="Full-time",
        monthly_income="20000-30000",
        household_size=3,
        children="Yes"
    )
    
    # Link customer profile to survey response
    survey_response.customer_profile = customer_profile
    
    # Initialize the service
    service = ReportGenerationService()
    
    try:
        print("=== Testing ReportGenerationService ===\n")
        
        # Test 1: Standard PDF report
        print("1. Testing standard PDF report generation...")
        pdf_content = await service.generate_pdf_report(
            survey_response=survey_response,
            language="en"
        )
        
        with open("service_test_standard.pdf", 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ Standard PDF generated: {len(pdf_content)} bytes")
        
        # Test 2: Summary report
        print("\n2. Testing summary report generation...")
        summary_content = await service.generate_summary_report(
            survey_response=survey_response,
            language="en"
        )
        
        with open("service_test_summary.pdf", 'wb') as f:
            f.write(summary_content)
        
        print(f"✅ Summary PDF generated: {len(summary_content)} bytes")
        
        # Test 3: Company branded report
        print("\n3. Testing company branded report...")
        company_branding = {
            'primary_color': '#0066cc',
            'secondary_color': '#00cc66',
            'accent_color': '#ff6600',
            'company_name': 'Emirates Financial Group',
            'website': 'www.emiratesfinancial.ae',
            'footer_text': 'Emirates Financial Group - Your trusted financial partner.',
            'show_charts': True,
            'chart_style': 'modern'
        }
        
        branded_content = await service.generate_company_branded_report(
            survey_response=survey_response,
            company_branding=company_branding,
            language="en"
        )
        
        with open("service_test_branded.pdf", 'wb') as f:
            f.write(branded_content)
        
        print(f"✅ Branded PDF generated: {len(branded_content)} bytes")
        
        # Test 4: Branded PDF from dictionary
        print("\n4. Testing branded PDF from dictionary...")
        survey_dict = {
            'id': 2,
            'user_id': 2,
            'responses': {
                'q1_income_stability': 5,
                'q2_income_sources': 4,
                'q3_living_expenses': 3,
            },
            'overall_score': 85,
            'budgeting_score': 90,
            'savings_score': 80,
            'debt_management_score': 85,
            'financial_planning_score': 85,
            'investment_knowledge_score': 75,
            'risk_tolerance': 'high',
            'profile': {
                'first_name': 'Omar',
                'last_name': 'Hassan',
                'age': 35,
                'nationality': 'UAE',
                'emirate': 'Dubai'
            }
        }
        
        branding_config = service.create_branding_config(
            primary_color="#8b5cf6",
            secondary_color="#10b981",
            company_name="Dubai Investment Solutions",
            website="www.dubaiinvestments.ae",
            show_charts=True
        )
        
        dict_content = await service.generate_branded_pdf(
            survey_data=survey_dict,
            branding_config=branding_config,
            language="en"
        )
        
        with open("service_test_from_dict.pdf", 'wb') as f:
            f.write(dict_content)
        
        print(f"✅ Dictionary-based PDF generated: {len(dict_content)} bytes")
        
        # Test 5: Arabic report
        print("\n5. Testing Arabic report generation...")
        arabic_content = await service.generate_pdf_report(
            survey_response=survey_response,
            language="ar"
        )
        
        with open("service_test_arabic.pdf", 'wb') as f:
            f.write(arabic_content)
        
        print(f"✅ Arabic PDF generated: {len(arabic_content)} bytes")
        
        # Test 6: Service capabilities
        print("\n6. Testing service capabilities...")
        formats = service.get_supported_formats()
        languages = service.get_supported_languages()
        
        print(f"✅ Supported formats: {formats}")
        print(f"✅ Supported languages: {languages}")
        
        # Test 7: Branding validation
        print("\n7. Testing branding validation...")
        
        # Valid config
        valid_config = {
            'primary_color': '#1e3a8a',
            'secondary_color': '#059669',
            'company_name': 'Test Company',
            'website': 'www.test.com',
            'chart_style': 'modern'
        }
        
        validation_result = service.validate_branding_config(valid_config)
        print(f"✅ Valid config validation: {validation_result}")
        
        # Invalid config
        invalid_config = {
            'primary_color': 'not-a-color',
            'chart_style': 'invalid-style',
            'website': 'not-a-url'
        }
        
        validation_result = service.validate_branding_config(invalid_config)
        print(f"✅ Invalid config validation: {validation_result}")
        
        # Test 8: Report metadata
        print("\n8. Testing report metadata generation...")
        metadata = await service.generate_report_metadata(
            survey_response=survey_response,
            report_type="standard",
            language="en"
        )
        
        print(f"✅ Report metadata generated:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 All ReportGenerationService tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in ReportGenerationService test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_report_generation_service())
    if success:
        print("\n✨ ReportGenerationService is working perfectly!")
    else:
        print("\n💥 ReportGenerationService test failed!")
        sys.exit(1)