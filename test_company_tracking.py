#!/usr/bin/env python3
"""
Test script for company tracking functionality.
Tests URL generation, QR code creation, and analytics.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.companies.qr_utils import generate_qr_code, get_qr_code_metadata

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@nationalbonds.ae"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Get admin authentication token."""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to authenticate admin: {response.status_code}")
        print(response.text)
        return None

def test_company_creation(token):
    """Test creating a new company."""
    headers = {"Authorization": f"Bearer {token}"}
    
    company_data = {
        "company_name": "Test Company Ltd",
        "company_email": "hr@testcompany.ae",
        "contact_person": "Ahmed Al-Rashid",
        "phone_number": "+971 4 123 4567"
    }
    
    response = requests.post(f"{BASE_URL}/companies/", 
                           json=company_data, 
                           headers=headers)
    
    if response.status_code == 200:
        company = response.json()
        print(f"✓ Company created successfully:")
        print(f"  ID: {company['id']}")
        print(f"  Name: {company['company_name']}")
        print(f"  Unique URL: {company['unique_url']}")
        return company
    else:
        print(f"✗ Failed to create company: {response.status_code}")
        print(response.text)
        return None

def test_url_generation(token, company_id):
    """Test generating company-specific URLs."""
    headers = {"Authorization": f"Bearer {token}"}
    
    config = {
        "expiry_days": 30,
        "max_responses": 1000,
        "custom_branding": True
    }
    
    response = requests.post(f"{BASE_URL}/companies/{company_id}/generate-link",
                           json=config,
                           headers=headers)
    
    if response.status_code == 200:
        link_data = response.json()
        print(f"✓ Company link generated successfully:")
        print(f"  URL: {link_data['url']}")
        print(f"  Expires: {link_data.get('expires_at', 'Never')}")
        print(f"  Max responses: {link_data.get('max_responses', 'Unlimited')}")
        return link_data
    else:
        print(f"✗ Failed to generate link: {response.status_code}")
        print(response.text)
        return None

def test_qr_code_generation():
    """Test QR code generation functionality."""
    print("\n=== Testing QR Code Generation ===")
    
    test_url = "https://financial-health.nationalbonds.ae/survey/c/testcompany"
    company_id = 1
    company_name = "Test Company Ltd"
    
    try:
        # Test base64 QR code generation
        qr_code_base64 = generate_qr_code(
            url=test_url,
            company_id=company_id,
            company_name=company_name,
            size=(300, 300)
        )
        
        print(f"✓ QR code generated successfully")
        print(f"  Format: Base64 PNG")
        print(f"  Size: ~{len(qr_code_base64)} characters")
        
        # Test metadata generation
        metadata = get_qr_code_metadata(test_url, company_id)
        print(f"✓ QR code metadata generated:")
        print(f"  URL: {metadata['url']}")
        print(f"  Company ID: {metadata['company_id']}")
        print(f"  Generated at: {metadata['generated_at']}")
        
        return True
        
    except Exception as e:
        print(f"✗ QR code generation failed: {str(e)}")
        return False

def test_company_analytics(token, company_id):
    """Test company analytics endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/companies/{company_id}/analytics",
                          headers=headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✓ Company analytics retrieved:")
        print(f"  Total responses: {analytics['total_responses']}")
        print(f"  Average score: {analytics.get('average_score', 'N/A')}")
        print(f"  At risk employees: {analytics['at_risk_employees']}")
        return analytics
    else:
        print(f"✗ Failed to get analytics: {response.status_code}")
        print(response.text)
        return None

def test_bulk_operations(token):
    """Test bulk company creation."""
    headers = {"Authorization": f"Bearer {token}"}
    
    bulk_data = {
        "companies": [
            {
                "company_name": "Emirates NBD",
                "company_email": "hr@emiratesnbd.com",
                "contact_person": "Sarah Al-Mansouri",
                "phone_number": "+971 4 316 0316"
            },
            {
                "company_name": "ADNOC Group",
                "company_email": "hr@adnoc.ae",
                "contact_person": "Mohammed Al-Jaber",
                "phone_number": "+971 2 202 0000"
            }
        ],
        "default_config": {
            "expiry_days": 60,
            "max_responses": 5000
        }
    }
    
    response = requests.post(f"{BASE_URL}/companies/bulk",
                           json=bulk_data,
                           headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Bulk operation completed:")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        if result.get('errors'):
            print(f"  Errors: {result['errors']}")
        return result
    else:
        print(f"✗ Bulk operation failed: {response.status_code}")
        print(response.text)
        return None

def main():
    """Run all company tracking tests."""
    print("=== Company Tracking System Test ===\n")
    
    # Test QR code generation (doesn't require server)
    qr_success = test_qr_code_generation()
    
    print("\n=== Testing API Endpoints ===")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("Cannot proceed without admin authentication")
        return
    
    print("✓ Admin authentication successful\n")
    
    # Test company creation
    company = test_company_creation(token)
    if not company:
        print("Cannot proceed without company creation")
        return
    
    print()
    
    # Test URL generation
    link_data = test_url_generation(token, company['id'])
    print()
    
    # Test analytics
    analytics = test_company_analytics(token, company['id'])
    print()
    
    # Test bulk operations
    bulk_result = test_bulk_operations(token)
    
    print("\n=== Test Summary ===")
    print(f"QR Code Generation: {'✓' if qr_success else '✗'}")
    print(f"Company Creation: {'✓' if company else '✗'}")
    print(f"URL Generation: {'✓' if link_data else '✗'}")
    print(f"Analytics: {'✓' if analytics else '✗'}")
    print(f"Bulk Operations: {'✓' if bulk_result else '✗'}")

if __name__ == "__main__":
    main()