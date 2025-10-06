"""Test script for the enhanced PDF report generation service."""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.reports.report_generation_service import ReportGenerationService
from app.reports.pdf_service import BrandingConfig
from app.models import SurveyResponse, CustomerProfile
from datetime import datetime


def create_mock_survey_response():
    """Create a mock survey response for testing."""
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
        first_name="Khalid",
        last_name="Al-Rashid",
        age=34,
        gender="Male",
        nationality="UAE",
        emirate="Sharjah",
        employment_status="Full-time",
        monthly_income="25000-35000",
        household_size=5,
        children="Yes"
    )
    
    # Link customer profile to survey response
    survey_response.customer_profile = customer_profile
    
    return survey_response


async def test_enhanced_pdf_features():
    """Test the enhanced PDF generation features."""
    
    print("🧪 Testing Enhanced PDF Report Generation")
    print("=" * 50)
    
    # Create test data
    survey_response = create_mock_survey_response()
    
    # Initialize service
    service = ReportGenerationService()
    
    test_results = {
        'standard_report': False,
        'charts_included': False,
        'custom_branding': False,
        'summary_report': False,
        'arabic_support': False,
        'multiple_formats': False
    }
    
    try:
        # Test 1: Standard report with charts
        print("\n📊 Test 1: Standard Report with Charts")
        print("-" * 30)
        
        pdf_content = await service.generate_pdf_report(
            survey_response=survey_response,
            language="en"
        )
        
        with open("enhanced_test_standard.pdf", 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ Standard report generated: {len(pdf_content)} bytes")
        test_results['standard_report'] = True
        test_results['charts_included'] = len(pdf_content) > 6000  # Charts should increase file size
        
        # Test 2: Custom branding
        print("\n🎨 Test 2: Custom Branding Configuration")
        print("-" * 30)
        
        custom_branding = {
            'primary_color': '#e11d48',  # Rose
            'secondary_color': '#059669',  # Emerald
            'accent_color': '#f59e0b',  # Amber
            'company_name': 'UAE Financial Advisory',
            'website': 'www.uaefinancial.ae',
            'footer_text': 'UAE Financial Advisory - Empowering your financial future.',
            'show_charts': True,
            'chart_style': 'modern'
        }
        
        branded_content = await service.generate_company_branded_report(
            survey_response=survey_response,
            company_branding=custom_branding,
            language="en"
        )
        
        with open("enhanced_test_branded.pdf", 'wb') as f:
            f.write(branded_content)
        
        print(f"✅ Branded report generated: {len(branded_content)} bytes")
        test_results['custom_branding'] = True
        
        # Test 3: Summary report
        print("\n📄 Test 3: Summary Report Format")
        print("-" * 30)
        
        summary_content = await service.generate_summary_report(
            survey_response=survey_response,
            language="en"
        )
        
        with open("enhanced_test_summary.pdf", 'wb') as f:
            f.write(summary_content)
        
        print(f"✅ Summary report generated: {len(summary_content)} bytes")
        test_results['summary_report'] = len(summary_content) < len(pdf_content)  # Should be smaller
        
        # Test 4: Arabic support
        print("\n🌍 Test 4: Arabic Language Support")
        print("-" * 30)
        
        arabic_content = await service.generate_pdf_report(
            survey_response=survey_response,
            language="ar"
        )
        
        with open("enhanced_test_arabic.pdf", 'wb') as f:
            f.write(arabic_content)
        
        print(f"✅ Arabic report generated: {len(arabic_content)} bytes")
        test_results['arabic_support'] = True
        
        # Test 5: Multiple format support
        print("\n🔧 Test 5: Multiple Format Support")
        print("-" * 30)
        
        formats = service.get_supported_formats()
        languages = service.get_supported_languages()
        
        print(f"✅ Supported formats: {formats}")
        print(f"✅ Supported languages: {languages}")
        
        test_results['multiple_formats'] = len(formats) >= 2 and len(languages) >= 2
        
        # Test 6: Branding validation
        print("\n✅ Test 6: Branding Configuration Validation")
        print("-" * 30)
        
        # Test valid configuration
        valid_config = {
            'primary_color': '#1e3a8a',
            'secondary_color': '#059669',
            'company_name': 'Test Company',
            'chart_style': 'modern'
        }
        
        validation = service.validate_branding_config(valid_config)
        print(f"Valid config result: {validation['valid']}")
        
        # Test invalid configuration
        invalid_config = {
            'primary_color': 'invalid-color',
            'chart_style': 'invalid-style'
        }
        
        validation = service.validate_branding_config(invalid_config)
        print(f"Invalid config detected: {not validation['valid']}")
        print(f"Errors found: {len(validation['errors'])}")
        
        # Test 7: Report metadata
        print("\n📋 Test 7: Report Metadata Generation")
        print("-" * 30)
        
        metadata = await service.generate_report_metadata(
            survey_response=survey_response,
            report_type="standard",
            language="en"
        )
        
        print(f"✅ Metadata generated with {len(metadata)} fields")
        print(f"   Report ID: {metadata['report_id']}")
        print(f"   Overall Score: {metadata['overall_score']}")
        print(f"   Estimated Pages: {metadata['estimated_pages']}")
        
        # Test 8: Dictionary-based generation
        print("\n📊 Test 8: Dictionary-based Report Generation")
        print("-" * 30)
        
        survey_dict = {
            'id': 2,
            'user_id': 2,
            'responses': {
                'q1_income_stability': 5,
                'q2_income_sources': 4,
            },
            'overall_score': 88,
            'budgeting_score': 90,
            'savings_score': 85,
            'debt_management_score': 90,
            'financial_planning_score': 85,
            'investment_knowledge_score': 80,
            'risk_tolerance': 'high',
            'profile': {
                'first_name': 'Aisha',
                'last_name': 'Mohammed',
                'age': 31,
                'nationality': 'UAE',
                'emirate': 'Dubai'
            }
        }
        
        branding_config = service.create_branding_config(
            primary_color="#6366f1",
            secondary_color="#10b981",
            company_name="Dubai Financial Solutions",
            show_charts=True
        )
        
        dict_content = await service.generate_branded_pdf(
            survey_data=survey_dict,
            branding_config=branding_config,
            language="en"
        )
        
        with open("enhanced_test_dict.pdf", 'wb') as f:
            f.write(dict_content)
        
        print(f"✅ Dictionary-based report generated: {len(dict_content)} bytes")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All enhanced PDF features are working perfectly!")
            return True
        else:
            print("⚠️  Some features need attention.")
            return False
        
    except Exception as e:
        print(f"❌ Error in enhanced PDF test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_pdf_features())
    if success:
        print("\n✨ Enhanced PDF service is ready for production!")
    else:
        print("\n💥 Enhanced PDF service test failed!")
        sys.exit(1)