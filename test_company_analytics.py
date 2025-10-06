#!/usr/bin/env python3
"""
Test company analytics and reporting functionality.
"""

import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@nationalbonds.ae"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    return response.json()["access_token"] if response.status_code == 200 else None

def create_test_companies(token):
    """Create test companies for analytics testing."""
    headers = {"Authorization": f"Bearer {token}"}
    
    companies_data = [
        {
            "company_name": "Emirates NBD Bank",
            "company_email": "hr@emiratesnbd.com",
            "contact_person": "Sarah Al-Mansouri",
            "phone_number": "+971 4 316 0316"
        },
        {
            "company_name": "ADNOC Group",
            "company_email": "hr@adnoc.ae", 
            "contact_person": "Mohammed Al-Jaber",
            "phone_number": "+971 2 202 0000"
        },
        {
            "company_name": "Dubai Municipality",
            "company_email": "hr@dm.gov.ae",
            "contact_person": "Fatima Al-Zahra",
            "phone_number": "+971 4 221 5555"
        }
    ]
    
    created_companies = []
    
    for company_data in companies_data:
        response = requests.post(f"{BASE_URL}/companies/", 
                               json=company_data, 
                               headers=headers)
        
        if response.status_code == 200:
            company = response.json()
            created_companies.append(company)
            print(f"✓ Created company: {company['company_name']} (ID: {company['id']})")
        else:
            print(f"✗ Failed to create company {company_data['company_name']}: {response.status_code}")
    
    return created_companies

def create_mock_assessments(token, company_id, count=10):
    """Create mock assessment data for testing analytics."""
    # This would normally be done through the survey endpoint
    # For testing, we'll use direct database insertion
    
    print(f"Note: Mock assessment creation would require survey completion endpoint")
    print(f"For full testing, complete {count} surveys for company {company_id}")
    
    return True

def test_company_analytics(token, company_id):
    """Test individual company analytics."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing Analytics for Company {company_id} ===")
    
    # Test basic analytics
    response = requests.get(f"{BASE_URL}/companies/{company_id}/analytics", 
                          headers=headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✓ Basic analytics retrieved:")
        print(f"  Company: {analytics['company_name']}")
        print(f"  Total responses: {analytics['total_responses']}")
        print(f"  Average score: {analytics.get('average_score', 'N/A')}")
        print(f"  At risk: {analytics['at_risk_employees']}")
        print(f"  Good health: {analytics['good_health']}")
        print(f"  Excellent: {analytics['excellent_health']}")
        
        if analytics.get('age_distribution'):
            print(f"  Age distribution: {analytics['age_distribution']}")
        if analytics.get('gender_distribution'):
            print(f"  Gender distribution: {analytics['gender_distribution']}")
        
        return analytics
    else:
        print(f"✗ Failed to get analytics: {response.status_code}")
        print(response.text)
        return None

def test_company_comparison(token, company_ids):
    """Test company comparison functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing Company Comparison ===")
    
    # Test comparison with multiple companies
    ids_str = ",".join(map(str, company_ids))
    response = requests.get(f"{BASE_URL}/companies/analytics/comparison?company_ids={ids_str}",
                          headers=headers)
    
    if response.status_code == 200:
        comparison = response.json()
        print(f"✓ Company comparison retrieved:")
        print(f"  Companies compared: {comparison['total_companies']}")
        print(f"  Benchmark average: {comparison['benchmark_average']}")
        
        for company_data in comparison['comparison_data']:
            print(f"  - {company_data['company_name']}: {company_data['average_score']} (vs benchmark: {company_data.get('vs_benchmark', 'N/A')})")
        
        return comparison
    else:
        print(f"✗ Failed to get comparison: {response.status_code}")
        print(response.text)
        return None

def test_companies_dashboard(token):
    """Test companies dashboard view."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing Companies Dashboard ===")
    
    # Test dashboard with different sorting options
    sort_options = [
        ("company_name", "asc"),
        ("total_responses", "desc"),
        ("average_score", "desc"),
        ("created_at", "desc")
    ]
    
    for sort_by, sort_order in sort_options:
        response = requests.get(
            f"{BASE_URL}/companies/analytics/dashboard?sort_by={sort_by}&sort_order={sort_order}&limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✓ Dashboard sorted by {sort_by} ({sort_order}):")
            print(f"  Total companies: {dashboard['summary']['total_companies']}")
            print(f"  Total assessments: {dashboard['summary']['total_assessments']}")
            print(f"  Overall average: {dashboard['summary']['overall_average_score']}")
            
            for company in dashboard['companies'][:3]:  # Show first 3
                print(f"  - {company['company_name']}: {company['total_assessments']} assessments, score: {company.get('average_score', 'N/A')}")
        else:
            print(f"✗ Failed to get dashboard with {sort_by} sort: {response.status_code}")
    
    return True

def test_date_filtering(token, company_id):
    """Test analytics with date filtering."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing Date Filtering for Company {company_id} ===")
    
    # Test with different date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(f"{BASE_URL}/companies/{company_id}/analytics",
                          params=params,
                          headers=headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✓ Analytics with date filter (last 30 days):")
        print(f"  Total responses: {analytics['total_responses']}")
        print(f"  Average score: {analytics.get('average_score', 'N/A')}")
        return analytics
    else:
        print(f"✗ Failed to get filtered analytics: {response.status_code}")
        return None

def main():
    """Run company analytics tests."""
    print("=== Company Analytics and Reporting Test ===\n")
    
    token = get_admin_token()
    if not token:
        print("Cannot proceed without admin authentication")
        return
    
    print("✓ Admin authentication successful\n")
    
    # Create test companies
    companies = create_test_companies(token)
    if not companies:
        print("Cannot proceed without companies")
        return
    
    company_ids = [c['id'] for c in companies]
    
    # Test individual company analytics
    analytics_results = []
    for company in companies[:2]:  # Test first 2 companies
        result = test_company_analytics(token, company['id'])
        if result:
            analytics_results.append(result)
    
    # Test company comparison
    if len(company_ids) >= 2:
        comparison_result = test_company_comparison(token, company_ids[:3])
    
    # Test companies dashboard
    dashboard_result = test_companies_dashboard(token)
    
    # Test date filtering
    if companies:
        date_filter_result = test_date_filtering(token, companies[0]['id'])
    
    print("\n=== Test Summary ===")
    print(f"Company Creation: {'✓' if companies else '✗'}")
    print(f"Individual Analytics: {'✓' if analytics_results else '✗'}")
    print(f"Company Comparison: {'✓' if len(company_ids) >= 2 and comparison_result else '✗'}")
    print(f"Dashboard View: {'✓' if dashboard_result else '✗'}")
    print(f"Date Filtering: {'✓' if date_filter_result else '✗'}")
    
    print(f"\nNote: To fully test analytics, complete some surveys using the company URLs:")
    for company in companies:
        print(f"  - {company['company_name']}: /survey/c/{company['unique_url']}")

if __name__ == "__main__":
    main()