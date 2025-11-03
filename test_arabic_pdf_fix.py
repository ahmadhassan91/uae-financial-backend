#!/usr/bin/env python3
"""
Test Arabic PDF generation with proper font support.
This script tests the Arabic text rendering in PDFs.
"""

import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.reports.report_generation_service import ReportGenerationService


def test_arabic_pdf():
    """Test Arabic PDF generation."""
    print("\n" + "="*70)
    print("TESTING ARABIC PDF GENERATION")
    print("="*70)
    
    service = ReportGenerationService()
    
    # Arabic test data
    survey_data_ar = {
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
                    'status_level': 'good',
                    'percentage': 80.0
                },
                {
                    'category': 'Savings Habit',
                    'category_ar': 'عادات الادخار',
                    'score': 13.0,
                    'max_possible': 15.0,
                    'status_level': 'excellent',
                    'percentage': 86.7
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
                    'score': 9.0,
                    'max_possible': 15.0,
                    'status_level': 'moderate',
                    'percentage': 60.0
                },
                {
                    'category': 'Protecting Your Family',
                    'category_ar': 'حماية عائلتك',
                    'score': 12.0,
                    'max_possible': 15.0,
                    'status_level': 'good',
                    'percentage': 80.0
                }
            ],
            'insights': [
                'لديك عادات ادخار ممتازة - استمر في هذا النهج الجيد',
                'إدارة ديونك في وضع جيد جداً',
                'يمكنك تحسين مدخرات التقاعد لضمان مستقبل أفضل',
                'مدخرات الطوارئ جيدة لكن حاول زيادتها لتغطية 6 أشهر',
                'تأمين حماية العائلة في مستوى جيد'
            ],
            'products': [
                {
                    'name': 'خطة التوفير المرنة',
                    'description': 'خطة ادخار بعوائد جذابة ومرونة عالية',
                    'relevance': 'تساعدك في بناء صندوق الطوارئ'
                },
                {
                    'name': 'تأمين الحماية الشاملة',
                    'description': 'تأمين شامل لحماية عائلتك ومستقبلك',
                    'relevance': 'يوفر الأمان المالي لعائلتك'
                }
            ]
        }
    }
    
    print("\n📄 Generating Arabic PDF with proper font support...")
    try:
        pdf_content = service.generate_financial_clinic_pdf(
            survey_data=survey_data_ar,
            language='ar'
        )
        
        # Save to file
        output_file = 'financial_clinic_arabic_fixed.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ Arabic PDF generated successfully!")
        print(f"   Size: {len(pdf_content):,} bytes")
        print(f"   Saved to: {output_file}")
        print(f"\n📋 PDF Details:")
        print(f"   - Profile Name: {survey_data_ar['profile']['name']}")
        print(f"   - Score: {survey_data_ar['result']['total_score']}/100")
        print(f"   - Categories: {len(survey_data_ar['result']['category_scores'])}")
        print(f"   - Insights: {len(survey_data_ar['result']['insights'])}")
        
        return True
    except Exception as e:
        print(f"❌ Arabic PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_arabic_support():
    """Check if Arabic support is available."""
    print("\n" + "="*70)
    print("CHECKING ARABIC SUPPORT")
    print("="*70)
    
    try:
        from arabic_reshaper import reshape
        from bidi.algorithm import get_display
        print("✅ arabic-reshaper library: INSTALLED")
        print("✅ python-bidi library: INSTALLED")
        arabic_libs = True
    except ImportError as e:
        print(f"❌ Arabic libraries: NOT INSTALLED")
        print(f"   Error: {e}")
        arabic_libs = False
    
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        print("✅ ReportLab TrueType fonts: SUPPORTED")
        reportlab_fonts = True
    except ImportError:
        print("❌ ReportLab TrueType fonts: NOT SUPPORTED")
        reportlab_fonts = False
    
    # Check for available fonts
    import os
    font_paths = [
        '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\DejaVuSans.ttf',
        '/Library/Fonts/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        'C:\\Windows\\Fonts\\ARIALUNI.TTF',
    ]
    
    print("\n📁 Checking for Arabic-compatible fonts:")
    fonts_found = []
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"   ✅ Found: {font_path}")
            fonts_found.append(font_path)
        else:
            print(f"   ❌ Not found: {font_path}")
    
    if fonts_found:
        print(f"\n✅ {len(fonts_found)} Arabic-compatible font(s) available")
    else:
        print("\n⚠️  No Arabic-compatible fonts found")
        print("   Recommendation: Install DejaVu Sans fonts")
    
    return arabic_libs and reportlab_fonts and len(fonts_found) > 0


def print_solution():
    """Print solution instructions."""
    print("\n" + "="*70)
    print("SOLUTION FOR ARABIC PDF RENDERING")
    print("="*70)
    
    print("\n✅ Implemented Solutions:")
    print("   1. Added arabic-reshaper library for text shaping")
    print("   2. Added python-bidi library for RTL text handling")
    print("   3. Registered TrueType fonts that support Arabic")
    print("   4. Updated PDF styles to use Arabic fonts")
    print("   5. Added text processing for Arabic content")
    
    print("\n📋 What's Happening:")
    print("   • Arabic text is reshaped for proper character joining")
    print("   • Bidirectional algorithm applies RTL display")
    print("   • Unicode-compatible fonts render Arabic glyphs")
    print("   • Text alignment is set to RIGHT for Arabic")
    
    print("\n🔧 If Arabic still doesn't display:")
    print("   1. Install DejaVu Sans fonts:")
    print("      brew install --cask font-dejavu  # macOS")
    print("      sudo apt-get install fonts-dejavu  # Linux")
    print("   2. Or use system fonts that support Arabic")
    print("   3. Restart the application after font installation")
    
    print("\n💡 Technical Details:")
    print("   • Font: DejaVu Sans (or Arial Unicode MS)")
    print("   • Encoding: Unicode (UTF-8)")
    print("   • Direction: RTL (Right-to-Left)")
    print("   • Shaping: Arabic Reshaper")
    print("   • Rendering: ReportLab with TTF fonts")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ARABIC PDF GENERATION - COMPLETE SOLUTION TEST")
    print("="*70)
    
    # Check support
    has_support = check_arabic_support()
    
    if not has_support:
        print("\n⚠️  WARNING: Some required components are missing!")
        print("   Arabic PDF may not render correctly.")
    
    # Show solution
    print_solution()
    
    # Test generation
    success = test_arabic_pdf()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if success:
        print("\n✅ ARABIC PDF GENERATION: SUCCESS")
        print("\n📂 Generated File:")
        print("   financial_clinic_arabic_fixed.pdf")
        print("\n💡 Next Steps:")
        print("   1. Open the PDF to verify Arabic text renders correctly")
        print("   2. Check that text is right-to-left")
        print("   3. Verify Arabic characters are properly shaped")
        print("   4. Test with different Arabic content")
    else:
        print("\n❌ ARABIC PDF GENERATION: FAILED")
        print("\n🔧 Troubleshooting:")
        print("   1. Check error messages above")
        print("   2. Ensure Arabic libraries are installed")
        print("   3. Verify fonts are available")
        print("   4. Check system font directories")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
