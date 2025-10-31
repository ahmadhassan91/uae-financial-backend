"""
Test Financial Clinic API Endpoints

This script tests the Financial Clinic API to ensure everything works correctly.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_questions():
    """Test GET /financial-clinic/questions"""
    print("\n" + "="*60)
    print("TEST 1: Get Financial Clinic Questions")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/financial-clinic/questions?has_children=true")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Got {len(data)} questions")
        print(f"  First question: {data[0]['text_en']}")
        print(f"  Last question: {data[-1]['text_en']}")
        print(f"  Q16 conditional: {data[-1]['conditional']}")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False


def test_calculate_score():
    """Test POST /financial-clinic/calculate"""
    print("\n" + "="*60)
    print("TEST 2: Calculate Financial Clinic Score")
    print("="*60)
    
    # Sample answers (all 4s = "Good" answers)
    request_data = {
        "answers": {
            "fc_q1": 4,
            "fc_q2": 4,
            "fc_q3": 4,
            "fc_q4": 4,
            "fc_q5": 4,
            "fc_q6": 4,
            "fc_q7": 4,
            "fc_q8": 4,
            "fc_q9": 4,
            "fc_q10": 4,
            "fc_q11": 4,
            "fc_q12": 4,
            "fc_q13": 4,
            "fc_q14": 4,
            "fc_q15": 4,
            "fc_q16": 4
        },
        "profile": {
            "name": "Test User",
            "email": "test@example.com",
            "date_of_birth": "1990-01-01",
            "nationality": "Emirati",
            "gender": "Female",
            "employment_status": "Full-time",
            "income_range": "10001-15000",
            "emirate": "Dubai",
            "children": 2
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/financial-clinic/calculate",
        json=request_data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"\n  Total Score: {data['total_score']}/100")
        print(f"  Status Band: {data['status_band']}")
        print(f"\n  Category Scores:")
        for category, score_data in data['category_scores'].items():
            print(f"    {category}: {score_data['score']:.1f}/{score_data['max_possible']:.0f} ({score_data['percentage']:.0f}%) - {score_data['status_level']}")
        print(f"\n  Insights ({len(data['insights'])}):")
        for insight in data['insights']:
            print(f"    - {insight['category']} ({insight['status_level']})")
        print(f"\n  Product Recommendations ({len(data['products'])}):")
        for product in data['products']:
            print(f"    - {product['name']} ({product['category']})")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False


def test_minimum_score():
    """Test with all 1s (worst answers)"""
    print("\n" + "="*60)
    print("TEST 3: Minimum Score (All 1s)")
    print("="*60)
    
    request_data = {
        "answers": {f"fc_q{i}": 1 for i in range(1, 17)},
        "profile": {
            "name": "Min Score User",
            "email": "min@example.com",
            "date_of_birth": "1985-05-15",
            "nationality": "Non-Emirati",
            "gender": "Male",
            "employment_status": "Unemployed",
            "income_range": "0-5000",
            "emirate": "Abu Dhabi",
            "children": 0
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/financial-clinic/calculate",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"  Total Score: {data['total_score']}/100")
        print(f"  Status Band: {data['status_band']}")
        print(f"  Expected: Score ~20, Status 'At Risk'")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False


def test_maximum_score():
    """Test with all 5s (best answers)"""
    print("\n" + "="*60)
    print("TEST 4: Maximum Score (All 5s)")
    print("="*60)
    
    request_data = {
        "answers": {f"fc_q{i}": 5 for i in range(1, 17)},
        "profile": {
            "name": "Max Score User",
            "email": "max@example.com",
            "date_of_birth": "1988-12-20",
            "nationality": "Emirati",
            "gender": "Female",
            "employment_status": "Full-time",
            "income_range": "25001-40000",
            "emirate": "Dubai",
            "children": 3
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/financial-clinic/calculate",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"  Total Score: {data['total_score']}/100")
        print(f"  Status Band: {data['status_band']}")
        print(f"  Expected: Score 100, Status 'Excellent'")
        
        # Check specific products for Emirati woman with children
        print(f"\n  Products for Emirati Woman with Children:")
        for product in data['products']:
            print(f"    - {product['name']}")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False


def test_stats():
    """Test GET /financial-clinic/stats"""
    print("\n" + "="*60)
    print("TEST 5: Get Statistics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/financial-clinic/stats")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success!")
        print(f"  Total Financial Clinic Surveys: {data['total_financial_clinic_surveys']}")
        print(f"  Active Products: {data['active_products']}")
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FINANCIAL CLINIC API TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the backend server is running on localhost:8000")
    
    try:
        # Run tests
        results = []
        results.append(("Get Questions", test_get_questions()))
        results.append(("Calculate Score", test_calculate_score()))
        results.append(("Minimum Score", test_minimum_score()))
        results.append(("Maximum Score", test_maximum_score()))
        results.append(("Get Stats", test_stats()))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for test_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        total = len(results)
        passed = sum(1 for _, p in results if p)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n✓ All tests passed! Financial Clinic API is working correctly.")
        else:
            print(f"\n✗ {total - passed} test(s) failed. Check the errors above.")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend server.")
        print("  Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
