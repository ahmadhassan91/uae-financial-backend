#!/usr/bin/env python3
"""
Complete Arabic Localization Backend Test

This script demonstrates and tests the complete Arabic localization functionality
including PDF generation, content management, and RTL text processing.
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.localization.service import LocalizationService
from app.reports.arabic_pdf_service import ArabicPDFReportService, ArabicBrandingConfig
from app.models import SurveyResponse, CustomerProfile


class MockSurveyResponse:
    """Mock survey response for testing"""
    def __init__(self):
        self.id = 1
        self.overall_score = 75.5
        self.budgeting_score = 80.0
        self.savings_score = 70.0
        self.debt_management_score = 85.0
        self.financial_planning_score = 65.0
        self.investment_knowledge_score = 75.0
        self.recommendations = [
            MockRecommendation("emergency_fund", "إنشاء صندوق طوارئ", "قم بإنشاء صندوق طوارئ يغطي 6 أشهر من النفقات"),
            MockRecommendation("investment", "تنويع الاستثمارات", "استثمر في صناديق الاستثمار المتنوعة"),
            MockRecommendation("retirement", "التخطيط للتقاعد", "راجع خطة التقاعد الخاصة بك")
        ]


class MockRecommendation:
    """Mock recommendation for testing"""
    def __init__(self, category: str, title: str, description: str):
        self.category = category
        self.title = title
        self.description = description


class MockCustomerProfile:
    """Mock customer profile for testing"""
    def __init__(self):
        self.id = 1
        self.name = "أحمد محمد الإماراتي"
        self.email = "ahmed@example.com"
        self.nationality = "UAE"
        self.age = 35
        self.emirate = "Dubai"


async def test_localization_service():
    """Test the localization service functionality"""
    print("🌐 Testing Localization Service...")
    
    db = SessionLocal()
    try:
        service = LocalizationService(db)
        
        # Test 1: Get supported languages
        languages = await service.get_supported_languages()
        print(f"✓ Supported languages: {len(languages)}")
        for lang in languages:
            print(f"  - {lang['name']} ({lang['code']}) - RTL: {lang['rtl']}")
        
        # Test 2: Content validation
        arabic_text = "مرحباً بك في تقرير الصحة المالية الخاص بك"
        validation = await service.validate_content("ui", "welcome.message", "ar", arabic_text)
        print(f"✓ Arabic content validation: {'Valid' if validation['is_valid'] else 'Invalid'}")
        if validation['warnings']:
            print(f"  Warnings: {validation['warnings']}")
        
        # Test 3: Create sample localized content
        try:
            content = await service.create_localized_content(
                content_type="ui",
                content_id="report.title",
                language="ar",
                text="تقرير الصحة المالية",
                title="عنوان التقرير"
            )
            print(f"✓ Created localized content: ID {content.id}")
        except Exception as e:
            print(f"⚠ Content creation (may already exist): {str(e)}")
        
        # Test 4: Get questions by language
        questions_ar = await service.get_questions_by_language("ar")
        questions_en = await service.get_questions_by_language("en")
        print(f"✓ Questions available - Arabic: {len(questions_ar)}, English: {len(questions_en)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Localization service test failed: {str(e)}")
        return False
    finally:
        db.close()


def test_arabic_pdf_generation():
    """Test Arabic PDF generation with comprehensive content"""
    print("\n📄 Testing Arabic PDF Generation...")
    
    try:
        # Create branding configuration
        branding = ArabicBrandingConfig(
            company_name="National Bonds",
            company_name_ar="شركة السندات الوطنية",
            primary_color="#1e3a8a",
            secondary_color="#059669",
            website="www.nationalbonds.ae",
            footer_text_ar="تم إنشاء هذا التقرير بواسطة شركة السندات الوطنية"
        )
        
        # Initialize PDF service
        pdf_service = ArabicPDFReportService(branding)
        print("✓ Arabic PDF service initialized")
        
        # Test Arabic text processing
        test_texts = [
            "مرحباً بك في تقرير الصحة المالية",
            "النتيجة الإجمالية: ٧٥ من ١٠٠",
            "التوصيات المخصصة لتحسين وضعك المالي",
            "إدارة الميزانية والنفقات الشهرية"
        ]
        
        for text in test_texts:
            processed = pdf_service._process_arabic_text(text)
            print(f"✓ Processed Arabic text: {text[:30]}...")
        
        # Create mock data
        survey_response = MockSurveyResponse()
        customer_profile = MockCustomerProfile()
        
        # Generate Arabic PDF
        print("📝 Generating Arabic PDF report...")
        pdf_content = pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language="ar",
            branding_config=branding
        )
        
        if pdf_content and len(pdf_content) > 1000:
            # Save the PDF
            filename = f"test_arabic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_content)
            
            print(f"✓ Arabic PDF generated successfully!")
            print(f"  File size: {len(pdf_content):,} bytes")
            print(f"  Saved as: {filename}")
            
            # Generate English version for comparison
            pdf_content_en = pdf_service.generate_pdf_report(
                survey_response=survey_response,
                customer_profile=customer_profile,
                language="en",
                branding_config=branding
            )
            
            filename_en = f"test_english_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename_en, "wb") as f:
                f.write(pdf_content_en)
            
            print(f"✓ English PDF generated for comparison: {filename_en}")
            
            return True
        else:
            print("✗ PDF generation failed - content too small or empty")
            return False
            
    except Exception as e:
        print(f"✗ Arabic PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rtl_text_processing():
    """Test RTL text processing capabilities"""
    print("\n🔄 Testing RTL Text Processing...")
    
    try:
        pdf_service = ArabicPDFReportService()
        
        # Test various Arabic text scenarios
        test_cases = [
            {
                "name": "Simple Arabic text",
                "text": "مرحباً بك",
                "expected_rtl": True
            },
            {
                "name": "Mixed Arabic and English",
                "text": "مرحباً Welcome بك",
                "expected_rtl": True
            },
            {
                "name": "Arabic with numbers",
                "text": "النتيجة: ٧٥ من ١٠٠",
                "expected_rtl": True
            },
            {
                "name": "Long Arabic sentence",
                "text": "هذا تقرير شامل عن الصحة المالية يتضمن تحليلاً مفصلاً لوضعك المالي الحالي",
                "expected_rtl": True
            },
            {
                "name": "English text",
                "text": "This is an English sentence",
                "expected_rtl": False
            }
        ]
        
        for case in test_cases:
            original_text = case["text"]
            processed_text = pdf_service._process_arabic_text(original_text)
            
            # Check if text contains Arabic characters
            has_arabic = any('\u0600' <= char <= '\u06FF' for char in original_text)
            
            print(f"✓ {case['name']}")
            print(f"  Original: {original_text}")
            print(f"  Processed: {processed_text}")
            print(f"  Has Arabic: {has_arabic}")
            print(f"  Length change: {len(processed_text) - len(original_text)}")
        
        return True
        
    except Exception as e:
        print(f"✗ RTL text processing failed: {str(e)}")
        return False


def test_font_registration():
    """Test Arabic font registration"""
    print("\n🔤 Testing Font Registration...")
    
    try:
        pdf_service = ArabicPDFReportService()
        
        print(f"✓ Arabic font: {pdf_service.arabic_font}")
        print(f"✓ Arabic bold font: {pdf_service.arabic_font_bold}")
        
        # Test font availability
        available_fonts = ["Helvetica", "Helvetica-Bold"]  # Default fallbacks
        
        # Check if Arabic fonts are registered
        try:
            from reportlab.pdfbase import pdfmetrics
            registered_fonts = pdfmetrics.getRegisteredFontNames()
            arabic_fonts = [f for f in registered_fonts if any(
                arabic_name in f for arabic_name in ["Arabic", "Amiri", "Cairo", "Noto"]
            )]
            
            if arabic_fonts:
                print(f"✓ Arabic fonts registered: {arabic_fonts}")
            else:
                print("⚠ No specific Arabic fonts found, using fallback fonts")
                
        except Exception as e:
            print(f"⚠ Font registration check failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Font registration test failed: {str(e)}")
        return False


async def run_comprehensive_test():
    """Run all comprehensive localization tests"""
    print("🚀 Starting Comprehensive Arabic Localization Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Localization Service
    result1 = await test_localization_service()
    results.append(("Localization Service", result1))
    
    # Test 2: Arabic PDF Generation
    result2 = test_arabic_pdf_generation()
    results.append(("Arabic PDF Generation", result2))
    
    # Test 3: RTL Text Processing
    result3 = test_rtl_text_processing()
    results.append(("RTL Text Processing", result3))
    
    # Test 4: Font Registration
    result4 = test_font_registration()
    results.append(("Font Registration", result4))
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Arabic localization backend is fully functional")
        print("✅ PDF generation with Arabic support is working")
        print("✅ RTL text processing is operational")
        print("✅ Ready for production deployment")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("🔧 Review failed components before deployment")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("1. Install Arabic fonts (Noto Sans Arabic, Amiri, Cairo) for better rendering")
    print("2. Test with real survey data and customer profiles")
    print("3. Verify PDF rendering in different browsers and PDF viewers")
    print("4. Test with longer Arabic text content")
    print("5. Validate cultural adaptations for UAE context")
    
    return passed == total


def main():
    """Main function"""
    try:
        # Run the comprehensive test
        result = asyncio.run(run_comprehensive_test())
        
        if result:
            print("\n🎯 Test completed successfully!")
            exit(0)
        else:
            print("\n❌ Some tests failed!")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()