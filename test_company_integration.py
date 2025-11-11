#!/usr/bin/env python3
"""
Test Company Integration with Financial Clinic

This script tests the complete flow of company-tracked Financial Clinic submissions.

Run from backend directory:
    python test_company_integration.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"  # Update with your admin credentials
ADMIN_PASSWORD = "admin123"  # Update with your admin password

def print_test_header(test_name):
    """Print formatted test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)

def print_result(success, message):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    return success

def test_1_create_test_company(token):
    """Test 1: Create a test company for tracking."""
    print_test_header("Create Test Company")
    
    company_data = {
        "company_name": "Test Financial Corp",
        "company_email": "hr@testfinancial.com",
        "contact_person": "HR Manager",
        "phone_number": "0501234567"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/companies/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=company_data
        )
        
        if response.status_code == 200:
            company = response.json()
            unique_url = company.get('unique_url')
            print_result(True, f"Company created with URL: {unique_url}")
            return unique_url
        else:
            print_result(False, f"Failed to create company: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return None

def test_2_validate_company_url(company_url):
    """Test 2: Validate company URL (public endpoint)."""
    print_test_header("Validate Company URL (Public)")
    
    try:
        response = requests.get(f"{API_BASE}/companies/by-url/{company_url}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Company validated: {data.get('company_name')}")
            return True
        else:
            print_result(False, f"Validation failed: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_3_submit_survey_with_company(company_url):
    """Test 3: Submit Financial Clinic survey with company tracking."""
    print_test_header("Submit Survey with Company Tracking")
    
    survey_data = {
        "answers": {
            "q1": 5, "q2": 4, "q3": 5, "q4": 3, "q5": 4,
            "q6": 5, "q7": 4, "q8": 3, "q9": 5, "q10": 4,
            "q11": 3, "q12": 5, "q13": 4, "q14": 5
        },
        "profile": {
            "name": "Test Employee",
            "date_of_birth": "15/05/1990",
            "gender": "Male",
            "nationality": "Emirati",
            "children": 0,
            "employment_status": "Employed",
            "income_range": "10K - 15K",
            "emirate": "Dubai",
            "email": "employee@testfinancial.com"
        },
        "company_url": company_url
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/financial-clinic/submit",
            headers={"Content-Type": "application/json"},
            json=survey_data
        )
        
        if response.status_code == 200:
            result = response.json()
            survey_id = result.get('survey_response_id')
            company_tracked = result.get('company_tracked', False)
            score = result.get('total_score')
            
            print_result(True, f"Survey submitted (ID: {survey_id}, Score: {score})")
            print_result(company_tracked, f"Company tracking: {company_tracked}")
            return survey_id
        else:
            print_result(False, f"Submission failed: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return None

def test_4_submit_multiple_surveys(company_url, count=5):
    """Test 4: Submit multiple surveys for analytics testing."""
    print_test_header(f"Submit {count} Additional Surveys")
    
    success_count = 0
    
    for i in range(count):
        survey_data = {
            "answers": {
                "q1": (i % 5) + 1, "q2": ((i+1) % 5) + 1, "q3": ((i+2) % 5) + 1,
                "q4": ((i+3) % 5) + 1, "q5": ((i+4) % 5) + 1, "q6": (i % 5) + 1,
                "q7": ((i+1) % 5) + 1, "q8": ((i+2) % 5) + 1, "q9": ((i+3) % 5) + 1,
                "q10": ((i+4) % 5) + 1, "q11": (i % 5) + 1, "q12": ((i+1) % 5) + 1,
                "q13": ((i+2) % 5) + 1, "q14": ((i+3) % 5) + 1
            },
            "profile": {
                "name": f"Test Employee {i+2}",
                "date_of_birth": f"{15+i}/05/{1990-i}",
                "gender": "Male" if i % 2 == 0 else "Female",
                "nationality": "Emirati" if i % 2 == 0 else "Non-Emirati",
                "children": i % 3,
                "employment_status": ["Employed", "Self-Employed", "Unemployed"][i % 3],
                "income_range": ["Below 5K", "5K - 10K", "10K - 15K", "15K - 20K", "Above 20K"][i % 5],
                "emirate": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"][i % 4],
                "email": f"employee{i+2}@testfinancial.com"
            },
            "company_url": company_url
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/financial-clinic/submit",
                headers={"Content-Type": "application/json"},
                json=survey_data
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"  Survey {i+1}/{count} submitted ✓")
            else:
                print(f"  Survey {i+1}/{count} failed ✗")
                
        except Exception as e:
            print(f"  Survey {i+1}/{count} error: {str(e)}")
    
    print_result(success_count == count, f"Submitted {success_count}/{count} surveys")
    return success_count

def test_5_get_company_analytics(company_url, token):
    """Test 5: Retrieve company analytics."""
    print_test_header("Get Company Analytics")
    
    try:
        response = requests.get(
            f"{API_BASE}/financial-clinic/company/{company_url}/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            analytics = response.json()
            
            print(f"\n📊 Analytics Summary:")
            print(f"  Company: {analytics.get('company_name')}")
            print(f"  Total Assessments: {analytics.get('total_assessments')}")
            print(f"  Average Score: {analytics.get('average_score')}")
            print(f"  Status Distribution: {analytics.get('status_distribution')}")
            
            demographics = analytics.get('demographic_breakdown', {})
            print(f"\n👥 Demographics:")
            print(f"  Gender: {list(demographics.get('by_gender', {}).keys())}")
            print(f"  Nationality: {list(demographics.get('by_nationality', {}).keys())}")
            print(f"  Employment: {list(demographics.get('by_employment', {}).keys())}")
            
            print_result(True, "Analytics retrieved successfully")
            return True
        else:
            print_result(False, f"Failed to get analytics: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_6_get_company_submissions(company_url, token):
    """Test 6: Get paginated submissions list."""
    print_test_header("Get Company Submissions")
    
    try:
        response = requests.get(
            f"{API_BASE}/financial-clinic/company/{company_url}/submissions?limit=3",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('total_count')
            submissions = data.get('submissions', [])
            
            print(f"\n📋 Submissions (showing {len(submissions)} of {total_count}):")
            for sub in submissions[:3]:
                print(f"  - ID: {sub['id']}, Score: {sub['total_score']}, "
                      f"Status: {sub['status_band']}")
            
            print_result(True, f"Retrieved {total_count} submissions")
            return True
        else:
            print_result(False, f"Failed to get submissions: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def get_admin_token():
    """Get admin authentication token."""
    print_test_header("Admin Authentication")
    
    try:
        # Try to login (adjust endpoint based on your auth system)
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('token')
            print_result(True, "Admin authenticated")
            return token
        else:
            print_result(False, f"Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return None

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPANY INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE}")
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("\n❌ Cannot proceed without admin authentication")
        print("Please update ADMIN_EMAIL and ADMIN_PASSWORD in this script")
        sys.exit(1)
    
    # Test 1: Create company
    company_url = test_1_create_test_company(admin_token)
    if not company_url:
        print("\n❌ Cannot proceed without company")
        sys.exit(1)
    
    # Test 2: Validate company URL
    if not test_2_validate_company_url(company_url):
        print("\n⚠️  Company validation failed, but continuing...")
    
    # Test 3: Submit first survey
    survey_id = test_3_submit_survey_with_company(company_url)
    if not survey_id:
        print("\n⚠️  First survey failed, but continuing...")
    
    # Test 4: Submit multiple surveys
    test_4_submit_multiple_surveys(company_url, count=5)
    
    # Test 5: Get analytics
    test_5_get_company_analytics(company_url, admin_token)
    
    # Test 6: Get submissions
    test_6_get_company_submissions(company_url, admin_token)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print(f"\n✅ Company URL for testing: {company_url}")
    print(f"📊 View analytics at: /admin/companies/{company_url}/analytics")
    print(f"🔗 Survey link: /company/{company_url}/financial-clinic")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
