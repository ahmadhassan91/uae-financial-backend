#!/usr/bin/env python3
"""
Test script for Financial Clinic PDF and Email functionality.
Tests both PDF generation and email sending with realistic data.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.reports.report_generation_service import ReportGenerationService
from app.reports.email_service import EmailReportService


def create_sample_financial_clinic_data(language: str = "en"):
    """Create sample Financial Clinic data for testing."""
    
    if language == "ar":
        return {
            'profile': {
                'name': 'أحمد محمد',
                'age': 35,
                'nationality': 'إماراتي',
                'emirate': 'دبي',
                'email': 'ahmed@example.com'
            },
            'result': {
                'total_score': 67.5,
                'status_band': 'Good',
                'status_level': 'good',
                'category_scores': [
                    {
                        'category': 'Income Stream',
                        'category_ar': 'تدفق الدخل',
                        'score': 15.0,
                        'max_possible': 20.0,
                        'status_level': 'good',
                        'percentage': 75.0
                    },
                    {
                        'category': 'Savings Habit',
                        'category_ar': 'عادات الادخار',
                        'score': 12.0,
                        'max_possible': 15.0,
                        'status_level': 'excellent',
                        'percentage': 80.0
                    },
                    {
                        'category': 'Emergency Savings',
                        'category_ar': 'مدخرات الطوارئ',
                        'score': 10.0,
                        'max_possible': 15.0,
                        'status_level': 'moderate',
                        'percentage': 66.7
                    },
                    {
                        'category': 'Debt Management',
                        'category_ar': 'إدارة الديون',
                        'score': 18.0,
                        'max_possible': 20.0,
                        'status_level': 'excellent',
                        'percentage': 90.0
                    },
                    {
                        'category': 'Retirement Planning',
                        'category_ar': 'التخطيط للتقاعد',
                        'score': 8.0,
                        'max_possible': 15.0,
                        'status_level': 'moderate',
                        'percentage': 53.3
                    },
                    {
                        'category': 'Protecting Your Family',
                        'category_ar': 'حماية عائلتك',
                        'score': 11.0,
                        'max_possible': 15.0,
                        'status_level': 'good',
                        'percentage': 73.3
                    }
                ],
                'insights': [
                    'لديك مدخرات طوارئ جيدة، لكن يمكنك زيادتها لتغطية 6 أشهر من النفقات',
                    'إدارة ديونك ممتازة - استمر في هذا النهج',
                    'فكر في بدء أو زيادة مساهماتك في التقاعد',
                    'راجع احتياجات التأمين الخاصة بك لحماية عائلتك بشكل أفضل',
                    'عاداتك في الادخار قوية جداً - حافظ عليها!'
                ],
                'products': [
                    {
                        'name': 'خطة التوفير',
                        'description': 'خطة ادخار مرنة بعوائد جذابة',
                        'relevance': 'يساعد في بناء صندوق الطوارئ'
                    },
                    {
                        'name': 'تأمين الحماية',
                        'description': 'تأمين شامل لحماية عائلتك',
                        'relevance': 'يوفر الأمان المالي لعائلتك'
                    }
                ]
            }
        }
    else:
        return {
            'profile': {
                'name': 'John Smith',
                'age': 35,
                'nationality': 'UAE National',
                'emirate': 'Dubai',
                'email': 'john@example.com'
            },
            'result': {
                'total_score': 67.5,
                'status_band': 'Good',
                'status_level': 'good',
                'category_scores': [
                    {
                        'category': 'Income Stream',
                        'category_ar': 'تدفق الدخل',
                        'score': 15.0,
                        'max_possible': 20.0,
                        'status_level': 'good',
                        'percentage': 75.0
                    },
                    {
                        'category': 'Savings Habit',
                        'category_ar': 'عادات الادخار',
                        'score': 12.0,
                        'max_possible': 15.0,
                        'status_level': 'excellent',
                        'percentage': 80.0
                    },
                    {
                        'category': 'Emergency Savings',
                        'category_ar': 'مدخرات الطوارئ',
                        'score': 10.0,
                        'max_possible': 15.0,
                        'status_level': 'moderate',
                        'percentage': 66.7
                    },
                    {
                        'category': 'Debt Management',
                        'category_ar': 'إدارة الديون',
                        'score': 18.0,
                        'max_possible': 20.0,
                        'status_level': 'excellent',
                        'percentage': 90.0
                    },
                    {
                        'category': 'Retirement Planning',
                        'category_ar': 'التخطيط للتقاعد',
                        'score': 8.0,
                        'max_possible': 15.0,
                        'status_level': 'moderate',
                        'percentage': 53.3
                    },
                    {
                        'category': 'Protecting Your Family',
                        'category_ar': 'حماية عائلتك',
                        'score': 11.0,
                        'max_possible': 15.0,
                        'status_level': 'good',
                        'percentage': 73.3
                    }
                ],
                'insights': [
                    'You have good emergency savings, but consider increasing to cover 6 months of expenses',
                    'Your debt management is excellent - keep up this approach',
                    'Consider starting or increasing your retirement contributions',
                    'Review your insurance needs to better protect your family',
                    'Your saving habits are very strong - maintain them!'
                ],
                'products': [
                    {
                        'name': 'Savings Plan',
                        'description': 'Flexible savings plan with attractive returns',
                        'relevance': 'Helps build your emergency fund'
                    },
                    {
                        'name': 'Protection Insurance',
                        'description': 'Comprehensive insurance to protect your family',
                        'relevance': 'Provides financial security for your family'
                    }
                ]
            }
        }


def test_pdf_generation():
    """Test PDF generation for Financial Clinic."""
    print("\n" + "="*60)
    print("TESTING PDF GENERATION")
    print("="*60)
    
    service = ReportGenerationService()
    
    # Test English PDF
    print("\n📄 Generating English PDF...")
    try:
        survey_data_en = create_sample_financial_clinic_data('en')
        pdf_content_en = service.generate_financial_clinic_pdf(
            survey_data=survey_data_en,
            language='en'
        )
        
        # Save to file
        output_file = 'financial_clinic_test_en.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_content_en)
        
        print(f"✅ English PDF generated successfully!")
        print(f"   Size: {len(pdf_content_en):,} bytes")
        print(f"   Saved to: {output_file}")
    except Exception as e:
        print(f"❌ English PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Arabic PDF
    print("\n📄 Generating Arabic PDF...")
    try:
        survey_data_ar = create_sample_financial_clinic_data('ar')
        pdf_content_ar = service.generate_financial_clinic_pdf(
            survey_data=survey_data_ar,
            language='ar'
        )
        
        # Save to file
        output_file = 'financial_clinic_test_ar.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_content_ar)
        
        print(f"✅ Arabic PDF generated successfully!")
        print(f"   Size: {len(pdf_content_ar):,} bytes")
        print(f"   Saved to: {output_file}")
    except Exception as e:
        print(f"❌ Arabic PDF generation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_email_generation():
    """Test email HTML generation (without actually sending)."""
    print("\n" + "="*60)
    print("TESTING EMAIL HTML GENERATION")
    print("="*60)
    
    email_service = EmailReportService()
    
    # Test English Email HTML
    print("\n📧 Generating English Email HTML...")
    try:
        survey_data_en = create_sample_financial_clinic_data('en')
        html_content = email_service._generate_financial_clinic_email_html(
            result=survey_data_en['result'],
            profile=survey_data_en['profile'],
            language='en'
        )
        
        # Save to file
        output_file = 'financial_clinic_email_test_en.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ English email HTML generated successfully!")
        print(f"   Size: {len(html_content):,} characters")
        print(f"   Saved to: {output_file}")
    except Exception as e:
        print(f"❌ English email HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Arabic Email HTML
    print("\n📧 Generating Arabic Email HTML...")
    try:
        survey_data_ar = create_sample_financial_clinic_data('ar')
        html_content = email_service._generate_financial_clinic_email_html(
            result=survey_data_ar['result'],
            profile=survey_data_ar['profile'],
            language='ar'
        )
        
        # Save to file
        output_file = 'financial_clinic_email_test_ar.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Arabic email HTML generated successfully!")
        print(f"   Size: {len(html_content):,} characters")
        print(f"   Saved to: {output_file}")
    except Exception as e:
        print(f"❌ Arabic email HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test plain text versions
    print("\n📝 Generating plain text versions...")
    try:
        text_en = email_service._generate_financial_clinic_email_text(
            result=survey_data_en['result'],
            profile=survey_data_en['profile'],
            language='en'
        )
        text_ar = email_service._generate_financial_clinic_email_text(
            result=survey_data_ar['result'],
            profile=survey_data_ar['profile'],
            language='ar'
        )
        print(f"✅ Plain text versions generated successfully!")
        print(f"   English: {len(text_en)} characters")
        print(f"   Arabic: {len(text_ar)} characters")
    except Exception as e:
        print(f"❌ Plain text generation failed: {e}")


def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n✅ All tests completed!")
    print("\nGenerated Files:")
    print("  📄 financial_clinic_test_en.pdf")
    print("  📄 financial_clinic_test_ar.pdf")
    print("  📧 financial_clinic_email_test_en.html")
    print("  📧 financial_clinic_email_test_ar.html")
    print("\nNext Steps:")
    print("  1. Open the PDF files to verify the layout and content")
    print("  2. Open the HTML files in a browser to preview the emails")
    print("  3. Test actual email sending by configuring SMTP settings")
    print("  4. Test the API endpoints using the frontend or Postman")
    print("\n" + "="*60)


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FINANCIAL CLINIC PDF & EMAIL TEST SUITE")
    print("="*60)
    
    # Test PDF generation
    test_pdf_generation()
    
    # Test email generation
    await test_email_generation()
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    asyncio.run(main())
