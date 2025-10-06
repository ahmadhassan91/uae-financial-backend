#!/usr/bin/env python3
"""
Test bulk company management features including CSV import/export and automated reporting.
"""

import requests
import json
import csv
import io
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@nationalbonds.ae"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    return response.json()["access_token"] if response.status_code == 200 else None

def test_csv_import(token):
    """Test CSV import functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== Testing CSV Import ===")
    
    # Create test CSV data
    csv_data = """company_name,company_email,contact_person,phone_number
Abu Dhabi Commercial Bank,hr@adcb.com,Ahmed Al-Rashid,+971 2 621 2222
First Abu Dhabi Bank,hr@fab.ae,Fatima Al-Zahra,+971 2 610 0000
Dubai Islamic Bank,hr@dib.ae,Mohammed Al-Maktoum,+971 4 609 2222
Mashreq Bank,hr@mashreq.com,Sarah Al-Mansouri,+971 4 424 4444
Commercial Bank of Dubai,hr@cbd.ae,Omar Al-Suwaidi,+971 4 230 0000"""
    
    # Test CSV import
    files = {"file": ("companies.csv", csv_data.encode('utf-8'), "text/csv")}
    
    response = requests.post(
        f"{BASE_URL}/companies/import-csv?generate_links=true&expiry_days=60&max_responses=2000",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ CSV import successful:")
        print(f"  Message: {result['message']}")
        print(f"  Successful: {result['result']['successful']}")
        print(f"  Failed: {result['result']['failed']}")
        if result['result']['generated_links']:
            print(f"  Generated {len(result['result']['generated_links'])} links")
        return result
    else:
        print(f"✗ CSV import failed: {response.status_code}")
        print(response.text)
        return None

def test_csv_export(token):
    """Test CSV export functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing CSV Export ===")
    
    # Test basic export
    response = requests.get(f"{BASE_URL}/companies/export-csv", headers=headers)
    
    if response.status_code == 200:
        csv_content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        print(f"✓ Basic CSV export successful:")
        print(f"  Exported {len(rows)} companies")
        print(f"  Columns: {', '.join(csv_reader.fieldnames)}")
        
        # Test export with analytics
        response = requests.get(f"{BASE_URL}/companies/export-csv?include_analytics=true", headers=headers)
        
        if response.status_code == 200:
            csv_content = response.content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)
            
            print(f"✓ Analytics CSV export successful:")
            print(f"  Exported {len(rows)} companies with analytics")
            print(f"  Columns: {', '.join(csv_reader.fieldnames)}")
            return True
        else:
            print(f"✗ Analytics export failed: {response.status_code}")
            return False
    else:
        print(f"✗ CSV export failed: {response.status_code}")
        return False

def test_bulk_operations(token):
    """Test bulk operations like link generation and updates."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Bulk Operations ===")
    
    # Get some company IDs for testing
    response = requests.get(f"{BASE_URL}/companies/?limit=5", headers=headers)
    if response.status_code != 200:
        print("✗ Cannot get companies for bulk testing")
        return False
    
    companies = response.json()
    if len(companies) < 2:
        print("✗ Need at least 2 companies for bulk testing")
        return False
    
    company_ids = [c['id'] for c in companies[:3]]
    
    # Test bulk link generation
    link_config = {
        "expiry_days": 45,
        "max_responses": 1500,
        "custom_branding": True
    }
    
    response = requests.post(
        f"{BASE_URL}/companies/bulk-generate-links",
        json={"company_ids": company_ids, "config": link_config},
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Bulk link generation successful:")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Generated {len(result['generated_links'])} links")
    else:
        print(f"✗ Bulk link generation failed: {response.status_code}")
        print(response.text)
        return False
    
    # Test bulk updates
    updates = [
        {"id": company_ids[0], "phone_number": "+971 4 999 0001"},
        {"id": company_ids[1], "phone_number": "+971 4 999 0002"}
    ]
    
    response = requests.post(
        f"{BASE_URL}/companies/bulk-update",
        json={"updates": updates},
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Bulk update successful:")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        return True
    else:
        print(f"✗ Bulk update failed: {response.status_code}")
        print(response.text)
        return False

def test_automated_reporting(token):
    """Test automated reporting functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Automated Reporting ===")
    
    # Get some companies for reporting
    response = requests.get(f"{BASE_URL}/companies/?limit=5", headers=headers)
    if response.status_code != 200:
        print("✗ Cannot get companies for reporting")
        return False
    
    companies = response.json()
    if len(companies) < 2:
        print("✗ Need at least 2 companies for reporting")
        return False
    
    company_ids = ",".join(str(c['id']) for c in companies[:3])
    
    # Test summary report
    response = requests.post(
        f"{BASE_URL}/companies/reports/generate?report_type=summary&company_ids={company_ids}",
        headers=headers
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"✓ Summary report generated:")
        print(f"  Report type: {report['report_type']}")
        print(f"  Total companies: {report['overview']['total_companies']}")
        print(f"  Companies with data: {report['overview']['companies_with_data']}")
        print(f"  Recommendations: {len(report['recommendations'])}")
    else:
        print(f"✗ Summary report failed: {response.status_code}")
        print(response.text)
        return False
    
    # Test detailed report
    response = requests.post(
        f"{BASE_URL}/companies/reports/generate?report_type=detailed&company_ids={company_ids}",
        headers=headers
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"✓ Detailed report generated:")
        print(f"  Report type: {report['report_type']}")
        print(f"  Companies analyzed: {len(report['companies'])}")
    else:
        print(f"✗ Detailed report failed: {response.status_code}")
        return False
    
    # Test comparison report
    response = requests.post(
        f"{BASE_URL}/companies/reports/generate?report_type=comparison&company_ids={company_ids}",
        headers=headers
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"✓ Comparison report generated:")
        print(f"  Report type: {report['report_type']}")
        print(f"  Companies compared: {report['benchmark']['companies_compared']}")
        print(f"  Benchmark score: {report['benchmark']['average_score']}")
    else:
        print(f"✗ Comparison report failed: {response.status_code}")
        return False
    
    # Test CSV export of report
    response = requests.post(
        f"{BASE_URL}/companies/reports/generate?report_type=summary&format=csv",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ CSV report export successful")
        return True
    else:
        print(f"✗ CSV report export failed: {response.status_code}")
        return False

def test_bulk_company_creation(token):
    """Test the enhanced bulk company creation."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Enhanced Bulk Creation ===")
    
    bulk_data = {
        "companies": [
            {
                "company_name": "National Bank of Ras Al Khaimah",
                "company_email": "hr@rakbank.ae",
                "contact_person": "Ali Al-Qasimi",
                "phone_number": "+971 7 206 2222"
            },
            {
                "company_name": "Union National Bank",
                "company_email": "hr@unb.ae",
                "contact_person": "Mariam Al-Suwaidi",
                "phone_number": "+971 2 677 2200"
            }
        ],
        "default_config": {
            "expiry_days": 90,
            "max_responses": 3000,
            "custom_branding": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/companies/bulk", json=bulk_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Enhanced bulk creation successful:")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        if result['generated_links']:
            print(f"  Generated {len(result['generated_links'])} links with QR codes")
            # Check if QR codes are included
            first_link = result['generated_links'][0]
            if first_link.get('qr_code_url'):
                print(f"  QR codes included: {len(first_link['qr_code_url'])} chars")
        return result
    else:
        print(f"✗ Enhanced bulk creation failed: {response.status_code}")
        print(response.text)
        return None

def main():
    """Run bulk management tests."""
    print("=== Bulk Company Management Test ===\n")
    
    token = get_admin_token()
    if not token:
        print("Cannot proceed without admin authentication")
        return
    
    print("✓ Admin authentication successful\n")
    
    # Test CSV import
    csv_import_result = test_csv_import(token)
    
    # Test CSV export
    csv_export_result = test_csv_export(token)
    
    # Test bulk operations
    bulk_ops_result = test_bulk_operations(token)
    
    # Test automated reporting
    reporting_result = test_automated_reporting(token)
    
    # Test enhanced bulk creation
    bulk_creation_result = test_bulk_company_creation(token)
    
    print("\n=== Test Summary ===")
    print(f"CSV Import: {'✓' if csv_import_result else '✗'}")
    print(f"CSV Export: {'✓' if csv_export_result else '✗'}")
    print(f"Bulk Operations: {'✓' if bulk_ops_result else '✗'}")
    print(f"Automated Reporting: {'✓' if reporting_result else '✗'}")
    print(f"Enhanced Bulk Creation: {'✓' if bulk_creation_result else '✗'}")

if __name__ == "__main__":
    main()