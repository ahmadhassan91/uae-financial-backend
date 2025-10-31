"""Test PDF and Email functionality for Financial Clinic."""
import sys
import requests
import json

# Test server URL
BASE_URL = "http://localhost:8000"

def test_pdf_generation():
    """Test PDF generation endpoint."""
    print("\n" + "="*60)
    print("TEST 1: PDF Generation")
    print("="*60)
    
    # Sample result data matching FinancialClinicResultResponse model
    payload = {
        "result": {
            "total_score": 68.0,
            "status_band": "Good",
            "overall_score": 68.0,
            "category_scores": {
                "income_stability": 70.0,
                "savings_investment": 60.0,
                "debt_management": 75.0,
                "financial_protection": 65.0,
                "financial_planning": 70.0
            },
            "insights": [
                {
                    "category": "debt_management",
                    "message_en": "Your debt management is excellent",
                    "message_ar": "إدارة ديونك ممتازة",
                    "priority": "high"
                }
            ],
            "products": [
                {
                    "name_en": "Savings Account",
                    "name_ar": "حساب التوفير",
                    "relevance_score": 0.9
                }
            ],
            "questions_answered": 16,
            "total_questions": 16
        },
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/report/pdf",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if it's actually a PDF
            if response.content.startswith(b'%PDF'):
                print("✅ PDF generated successfully!")
                
                # Save PDF for manual inspection
                with open('test_financial_clinic_report.pdf', 'wb') as f:
                    f.write(response.content)
                print("📄 PDF saved as 'test_financial_clinic_report.pdf'")
            else:
                # It's a JSON response (service message)
                print("📋 Response:", response.json())
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return response.status_code == 200

def test_email_sending():
    """Test email sending endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Email Sending")
    print("="*60)
    
    payload = {
        "result": {
            "total_score": 68.0,
            "status_band": "Good",
            "overall_score": 68.0,
            "category_scores": {
                "income_stability": 70.0,
                "savings_investment": 60.0,
                "debt_management": 75.0,
                "financial_protection": 65.0,
                "financial_planning": 70.0
            },
            "insights": [
                {
                    "category": "debt_management",
                    "message_en": "Your debt management is excellent",
                    "message_ar": "إدارة ديونك ممتازة",
                    "priority": "high"
                }
            ],
            "products": [
                {
                    "name_en": "Savings Account",
                    "name_ar": "حساب التوفير",
                    "relevance_score": 0.9
                }
            ],
            "questions_answered": 16,
            "total_questions": 16
        },
        "email": "test@example.com",
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/report/email",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📧 Email Response:", json.dumps(result, indent=2))
            
            if result.get('success'):
                print("✅ Email sent successfully!")
            else:
                print("📋 Email service message:", result.get('message'))
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return response.status_code == 200

def run_all_tests():
    """Run all tests."""
    print("\n🧪 Financial Clinic PDF & Email Tests")
    print("Make sure the backend is running on port 8000")
    
    results = {
        "PDF Generation": test_pdf_generation(),
        "Email Sending": test_email_sending()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
