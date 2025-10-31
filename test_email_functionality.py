"""Test Financial Clinic Email Functionality"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_email():
    """Test the Financial Clinic email functionality."""
    from app.reports.email_service import EmailReportService
    from app.reports.pdf_service import PDFReportService
    
    print("\n🧪 Testing Financial Clinic Email Functionality")
    print("=" * 60)
    
    # Sample Financial Clinic result data
    test_result = {
        'total_score': 66.0,
        'status_band': 'Good',
        'status_level': 'good',
        'category_scores': [
            {
                'category': 'Income Stream',
                'category_ar': 'مجرى الدخل',
                'score': 9.0,
                'max_possible': 15.0,
                'percentage': 60.0,
                'status_level': 'good'
            },
            {
                'category': 'Savings & Investments',
                'category_ar': 'المدخرات والاستثمارات',
                'score': 12.0,
                'max_possible': 15.0,
                'percentage': 80.0,
                'status_level': 'excellent'
            },
            {
                'category': 'Debt Management',
                'category_ar': 'إدارة الديون',
                'score': 11.0,
                'max_possible': 15.0,
                'percentage': 73.33,
                'status_level': 'good'
            },
            {
                'category': 'Financial Protection',
                'category_ar': 'الحماية المالية',
                'score': 10.0,
                'max_possible': 15.0,
                'percentage': 66.67,
                'status_level': 'good'
            },
            {
                'category': 'Financial Planning',
                'category_ar': 'التخطيط المالي',
                'score': 12.0,
                'max_possible': 20.0,
                'percentage': 60.0,
                'status_level': 'good'
            },
            {
                'category': 'Financial Knowledge',
                'category_ar': 'المعرفة المالية',
                'score': 12.0,
                'max_possible': 20.0,
                'percentage': 60.0,
                'status_level': 'good'
            }
        ]
    }
    
    test_profile = {
        'name': 'Ahmad Hassan',
        'email': 'ahmad.hassan@clustox.com',
        'date_of_birth': '29/02/1991',
        'gender': 'Male',
        'nationality': 'Emirati',
        'emirates': 'Dubai',
        'employment_status': 'Self-Employed',
        'income_range': 'Below 5K',
        'mobile_number': '+972542865966',
        'children': 0
    }
    
    # Test 1: Generate PDF
    print("\n1. Generating PDF...")
    from app.reports.report_generation_service import ReportGenerationService
    service = ReportGenerationService()
    try:
        survey_data = {
            'result': test_result,
            'profile': test_profile
        }
        pdf_content = service.generate_financial_clinic_pdf(
            survey_data=survey_data,
            language='en'
        )
        print(f"   ✅ PDF generated successfully ({len(pdf_content)} bytes)")
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Generate Email HTML
    print("\n2. Generating Email HTML...")
    email_service = EmailReportService()
    try:
        html_content = email_service._generate_financial_clinic_email_html(
            result=test_result,
            profile=test_profile,
            language='en'
        )
        print(f"   ✅ Email HTML generated ({len(html_content)} characters)")
        
        # Save HTML to file for preview
        with open('/tmp/test_email.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   📄 Preview saved to: /tmp/test_email.html")
    except Exception as e:
        print(f"   ❌ Email HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Test Email Sending (without actually sending)
    print("\n3. Testing Email Preparation...")
    try:
        result = await email_service.send_financial_clinic_report(
            recipient_email=test_profile['email'],
            result=test_result,
            pdf_content=pdf_content,
            profile=test_profile,
            language='en'
        )
        
        if result['success']:
            print(f"   ✅ Email prepared successfully")
            print(f"      Recipient: {result['recipient']}")
            print(f"      Subject: {result['subject']}")
            print(f"      PDF Size: {result['attachment_size']} bytes")
        else:
            print(f"   ⚠️  Email preparation result: {result['message']}")
            print(f"      Note: This is expected if SMTP is not configured")
    except Exception as e:
        print(f"   ⚠️  Email sending note: {e}")
        print(f"      This is expected if SMTP credentials are not configured")
    
    print("\n" + "=" * 60)
    print("✅ Email Functionality Tests Complete!")
    print("\nNOTE: Actual email sending requires SMTP configuration.")
    print("The email HTML has been saved to /tmp/test_email.html for preview.")
    print("\n")

if __name__ == "__main__":
    asyncio.run(test_email())
