#!/usr/bin/env python3
"""
Test Arabic PDF generation for Financial Clinic with proper font support.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.reports.report_generation_service import ReportGenerationService


def create_arabic_test_data():
    """Create comprehensive Arabic test data."""
    return {
        'profile': {
            'name': 'أحمد محمد علي',
            'age': 35,
            'nationality': 'إماراتي',
            'emirate': 'دبي',
            'email': 'ahmed@example.com'
        },
        'result': {
            'total_score': 72.5,
            'status_band': 'Good',
            'status_level': 'good',
            'category_scores': [
                {
                    'category': 'Income Stream',
                    'category_ar': 'تدفق الدخل',
                    'score': 16.0,
                    'max_possible': 20.0,
                    'status_level': 'excellent',
                    'percentage': 80.0
                },
                {
                    'category': 'Savings Habit',
                    'category_ar': 'عادات الادخار',
                    'score': 12.5,
                    'max_possible': 15.0,
                    'status_level': 'excellent',
                    'percentage': 83.3
                },
                {
                    'category': 'Emergency Savings',
                    'category_ar': 'مدخرات الطوارئ',
                    'score': 11.0,
                    'max_possible': 15.0,
                    'status_level': 'good',
                    'percentage': 73.3
                },
                {
                    'category': 'Debt Management',
                    'category_ar': 'إدارة الديون',
                    'score': 17.0,
                    'max_possible': 20.0,
                    'status_level': 'excellent',
                    'percentage': 85.0
                },
                {
                    'category': 'Retirement Planning',
                    'category_ar': 'التخطيط للتقاعد',
                    'score': 10.0,
                    'max_possible': 15.0,
                    'status_level': 'moderate',
                    'percentage': 66.7
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
            'products': []
        }
    }


def main():
    """Generate Arabic PDF with proper font support."""
    print("\n" + "="*70)
    print("TESTING ARABIC PDF GENERATION WITH FONTS")
    print("="*70 + "\n")
    
    # Check if Arabic support is available
    from app.reports.pdf_service import ARABIC_SUPPORT, ARABIC_FONTS_AVAILABLE
    
    print(f"Arabic reshaping libraries: {'✅ Available' if ARABIC_SUPPORT else '❌ Not available'}")
    print(f"Arabic fonts registered: {'✅ Available' if ARABIC_FONTS_AVAILABLE else '❌ Not available'}")
    
    if not ARABIC_SUPPORT:
        print("\n⚠️  Warning: Arabic reshaping libraries not available.")
        print("   Install with: pip install arabic-reshaper python-bidi")
    
    if not ARABIC_FONTS_AVAILABLE:
        print("\n⚠️  Warning: Arabic fonts not found on system.")
        print("   Arabic text may not display correctly.")
    
    print("\n" + "-"*70)
    
    # Generate Arabic PDF
    print("\n📄 Generating Arabic PDF...")
    try:
        service = ReportGenerationService()
        test_data = create_arabic_test_data()
        
        pdf_content = service.generate_financial_clinic_pdf(
            survey_data=test_data,
            language='ar'
        )
        
        # Save PDF
        output_file = 'financial_clinic_arabic_fixed.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ Arabic PDF generated successfully!")
        print(f"   Size: {len(pdf_content):,} bytes")
        print(f"   Saved to: {output_file}")
        
        # Test English PDF for comparison
        print("\n📄 Generating English PDF for comparison...")
        pdf_content_en = service.generate_financial_clinic_pdf(
            survey_data=test_data,
            language='en'
        )
        
        output_file_en = 'financial_clinic_english_comparison.pdf'
        with open(output_file_en, 'wb') as f:
            f.write(pdf_content_en)
        
        print(f"✅ English PDF generated successfully!")
        print(f"   Size: {len(pdf_content_en):,} bytes")
        print(f"   Saved to: {output_file_en}")
        
        print("\n" + "="*70)
        print("SUCCESS! PDFs generated.")
        print("="*70)
        print("\nOpen the files to verify:")
        print(f"  open {output_file}")
        print(f"  open {output_file_en}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
