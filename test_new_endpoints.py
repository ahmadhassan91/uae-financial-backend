"""Test new Financial Clinic endpoints without breaking existing functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_existing_endpoint():
    """Test that existing calculate endpoint still works."""
    print("\n✅ Step 1: Testing EXISTING calculate endpoint...")
    
    payload = {
        "answers": {
            "fc_q1": 4,
            "fc_q2": 3,
            "fc_q3": 4,
            "fc_q4": 3,
            "fc_q5": 4,
            "fc_q6": 3,
            "fc_q7": 3,
            "fc_q8": 2,
            "fc_q9": 3,
            "fc_q10": 5,
            "fc_q11": 4,
            "fc_q12": 4,
            "fc_q13": 2,
            "fc_q14": 3,
            "fc_q15": 3,
            "fc_q16": 4
        },
        "profile": {
            "name": "Test User",
            "date_of_birth": "15/05/1990",
            "gender": "Male",
            "nationality": "Emirati",
            "children": 2,
            "employment_status": "Employed",
            "income_range": "15K-25K",
            "emirate": "Dubai",
            "email": "test@example.com",
            "mobile_number": "+971501234567"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/calculate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Calculate endpoint works!")
            print(f"   ✓ Score: {result['total_score']}/100")
            print(f"   ✓ Status: {result['status_band']}")
            print(f"   ✓ Insights: {len(result['insights'])} insights")
            print(f"   ✓ Products: {len(result['products'])} products")
            return True, result
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            print(f"   ✗ Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False, None


def test_pdf_endpoint(result_data):
    """Test new PDF endpoint (expect it to return error about missing service for now)."""
    print("\n📄 Step 2: Testing NEW PDF endpoint...")
    
    payload = {
        "result": result_data,
        "profile": {
            "name": "Test User",
            "date_of_birth": "15/05/1990",
            "gender": "Male",
            "nationality": "Emirati",
            "children": 2,
            "employment_status": "Employed",
            "income_range": "15K-25K",
            "emirate": "Dubai",
            "email": "test@example.com"
        },
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/report/pdf",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 501:
            print("   ✓ Expected: PDF service not yet configured")
            print("   ✓ Endpoint is reachable and handling requests correctly")
            return True
        elif response.status_code == 200:
            print("   ✓ PDF generated successfully!")
            print(f"   ✓ Size: {len(response.content)} bytes")
            return True
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False


def test_email_endpoint(result_data):
    """Test new email endpoint."""
    print("\n📧 Step 3: Testing NEW email endpoint...")
    
    payload = {
        "result": result_data,
        "email": "test@example.com",
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial-clinic/report/email",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Response: {data.get('message', 'No message')}")
            if data.get('note'):
                print(f"   ℹ Note: {data['note']}")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("Testing New Financial Clinic Endpoints")
    print("=" * 60)
    print("\nThis test verifies:")
    print("1. Existing endpoints still work (no breaking changes)")
    print("2. New PDF endpoint is accessible")
    print("3. New email endpoint is accessible")
    print("\n" + "=" * 60)
    
    # Test 1: Existing endpoint
    success, result_data = test_existing_endpoint()
    if not success:
        print("\n❌ CRITICAL: Existing endpoint broken! Stopping tests.")
        return
    
    # Test 2: New PDF endpoint
    pdf_success = test_pdf_endpoint(result_data)
    
    # Test 3: New email endpoint
    email_success = test_email_endpoint(result_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Existing Calculate Endpoint: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"New PDF Endpoint:            {'✅ PASS' if pdf_success else '❌ FAIL'}")
    print(f"New Email Endpoint:          {'✅ PASS' if email_success else '❌ FAIL'}")
    print("\n" + "=" * 60)
    
    if success and pdf_success and email_success:
        print("✅ All tests passed! No breaking changes detected.")
    else:
        print("⚠️  Some tests failed. Review output above.")


if __name__ == "__main__":
    main()
