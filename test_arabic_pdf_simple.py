"""Simple test for Arabic PDF generation without database dependencies."""
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.reports.arabic_pdf_service import ArabicPDFReportService, ArabicBrandingConfig


def test_arabic_text_processing():
    """Test Arabic text processing functionality."""
    print("Testing Arabic Text Processing...")
    
    # Create PDF service
    branding_config = ArabicBrandingConfig(
        company_name="National Bonds Corporation",
        company_name_ar="شركة السندات الوطنية",
        primary_color="#1e3a8a",
        secondary_color="#059669"
    )
    
    pdf_service = ArabicPDFReportService(branding_config)
    
    # Test Arabic text processing
    test_texts = [
        "مرحباً بك في تقرير الصحة المالية",
        "درجة الصحة المالية",
        "التوصيات المخصصة",
        "تحسين إدارة الميزانية",
        "بناء صندوق الطوارئ",
        "إدارة الديون بفعالية"
    ]
    
    print("Arabic text processing results:")
    for text in test_texts:
        processed = pdf_service._process_arabic_text(text)
        print(f"  Original: {text}")
        print(f"  Processed: {processed}")
        print()
    
    # Test font registration
    print(f"Arabic font registered: {pdf_service.arabic_font}")
    print(f"Arabic bold font registered: {pdf_service.arabic_font_bold}")
    
    print("✓ Arabic text processing test completed!")


def test_font_registration():
    """Test font registration functionality."""
    print("\nTesting Font Registration...")
    
    pdf_service = ArabicPDFReportService()
    
    # Check if fonts were registered
    print(f"Arabic font: {pdf_service.arabic_font}")
    print(f"Arabic bold font: {pdf_service.arabic_font_bold}")
    
    # Test if fonts are available
    try:
        from reportlab.pdfbase import pdfmetrics
        available_fonts = pdfmetrics.getRegisteredFontNames()
        print(f"Total registered fonts: {len(available_fonts)}")
        
        arabic_fonts = [font for font in available_fonts if 'Arabic' in font or 'Amiri' in font or 'Cairo' in font]
        if arabic_fonts:
            print(f"Arabic fonts found: {arabic_fonts}")
        else:
            print("No specific Arabic fonts found, using fallback fonts")
        
    except Exception as e:
        print(f"Error checking fonts: {e}")
    
    print("✓ Font registration test completed!")


def test_branding_config():
    """Test branding configuration."""
    print("\nTesting Branding Configuration...")
    
    # Test default config
    default_config = ArabicBrandingConfig()
    print(f"Default company name (EN): {default_config.company_name}")
    print(f"Default company name (AR): {default_config.company_name_ar}")
    print(f"Primary color: {default_config.primary_color}")
    
    # Test custom config
    custom_config = ArabicBrandingConfig(
        company_name="Test Company",
        company_name_ar="شركة الاختبار",
        primary_color="#ff0000",
        secondary_color="#00ff00",
        footer_text_ar="نص تذييل مخصص"
    )
    
    print(f"Custom company name (EN): {custom_config.company_name}")
    print(f"Custom company name (AR): {custom_config.company_name_ar}")
    print(f"Custom footer (AR): {custom_config.footer_text_ar}")
    
    print("✓ Branding configuration test completed!")


def main():
    """Run all simple tests."""
    print("=== Arabic PDF Simple Tests ===")
    
    test_arabic_text_processing()
    test_font_registration()
    test_branding_config()
    
    print("\n🎉 All simple tests completed successfully!")
    print("\nNote: To test full PDF generation, use the main test script with proper database setup.")


if __name__ == "__main__":
    main()