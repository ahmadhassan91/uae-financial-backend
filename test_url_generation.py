#!/usr/bin/env python3
"""
Test URL generation, expiration, and renewal functionality.
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import time

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
        return None

def test_url_generation_unlimited(token):
    """Test generating unlimited unique URLs."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== Testing Unlimited URL Generation ===")
    
    # Create multiple companies with similar names
    companies = []
    base_names = [
        "Emirates Bank",
        "Emirates Bank Ltd", 
        "Emirates Bank Group",
        "National Bank UAE",
        "National Bank UAE Ltd"
    ]
    
    for i, name in enumerate(base_names):
        company_data = {
            "company_name": name,
            "company_email": f"hr{i}@{name.lower().replace(' ', '')}.ae",
            "contact_person": f"Contact Person {i+1}",
            "phone_number": f"+971 4 123 456{i}"
        }
        
        response = requests.post(f"{BASE_URL}/companies/", 
                               json=company_data, 
                               headers=headers)
        
        if response.status_code == 200:
            company = response.json()
            companies.append(company)
            print(f"✓ Created company: {company['company_name']} -> URL: {company['unique_url']}")
        else:
            print(f"✗ Failed to create company {name}: {response.status_code}")
    
    # Verify all URLs are unique
    urls = [c['unique_url'] for c in companies]
    unique_urls = set(urls)
    
    if len(urls) == len(unique_urls):
        print(f"✓ All {len(companies)} companies have unique URLs")
    else:
        print(f"✗ URL collision detected! {len(urls)} companies, {len(unique_urls)} unique URLs")
    
    return companies

def test_qr_code_generation(token, company_id):
    """Test QR code generation with different configurations."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing QR Code Generation for Company {company_id} ===")
    
    # Test different QR code configurations
    configs = [
        {"expiry_days": 7, "max_responses": 100},
        {"expiry_days": 30, "max_responses": 1000},
        {"expiry_days": 90, "max_responses": 5000},
        {"custom_branding": True}
    ]
    
    for i, config in enumerate(configs):
        response = requests.post(f"{BASE_URL}/companies/{company_id}/generate-link",
                               json=config,
                               headers=headers)
        
        if response.status_code == 200:
            link_data = response.json()
            qr_size = len(link_data.get('qr_code_url', ''))
            print(f"✓ Config {i+1}: QR code generated ({qr_size} chars)")
            print(f"  Expires: {link_data.get('expires_at', 'Never')}")
            print(f"  Max responses: {link_data.get('max_responses', 'Unlimited')}")
        else:
            print(f"✗ Config {i+1} failed: {response.status_code}")
    
    return True

def test_url_expiration_and_renewal(token, company_id):
    """Test URL expiration and renewal functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing URL Expiration and Renewal for Company {company_id} ===")
    
    # Generate a link with very short expiry for testing
    config = {
        "expiry_days": 0,  # This should create an immediately expired link
        "max_responses": 100
    }
    
    response = requests.post(f"{BASE_URL}/companies/{company_id}/generate-link",
                           json=config,
                           headers=headers)
    
    if response.status_code == 200:
        link_data = response.json()
        print(f"✓ Generated link with immediate expiry")
        print(f"  URL: {link_data['url']}")
        print(f"  Expires: {link_data.get('expires_at')}")
    else:
        print(f"✗ Failed to generate expiring link: {response.status_code}")
        return False
    
    # Check link status
    response = requests.get(f"{BASE_URL}/companies/{company_id}/link-status",
                          headers=headers)
    
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Link status retrieved:")
        print(f"  Active: {status['has_active_link']}")
        print(f"  Expired: {status['is_expired']}")
        print(f"  Current responses: {status['current_responses']}")
    else:
        print(f"✗ Failed to get link status: {response.status_code}")
        return False
    
    # Try to renew the expired link
    renewal_config = {
        "expiry_days": 30,
        "max_responses": 1000
    }
    
    response = requests.post(f"{BASE_URL}/companies/{company_id}/renew-link",
                           json=renewal_config,
                           headers=headers)
    
    if response.status_code == 200:
        renewed_link = response.json()
        print(f"✓ Link renewed successfully")
        print(f"  New expiry: {renewed_link.get('expires_at')}")
        print(f"  Max responses: {renewed_link.get('max_responses')}")
    else:
        print(f"✗ Failed to renew link: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # Verify renewed link status
    response = requests.get(f"{BASE_URL}/companies/{company_id}/link-status",
                          headers=headers)
    
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Renewed link status:")
        print(f"  Active: {status['has_active_link']}")
        print(f"  Expired: {status['is_expired']}")
    else:
        print(f"✗ Failed to get renewed link status: {response.status_code}")
        return False
    
    return True

def test_custom_url_prefixes(token, company_id):
    """Test custom URL prefix functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== Testing Custom URL Prefixes for Company {company_id} ===")
    
    # Test custom prefixes
    custom_prefixes = [
        "emirates-bank-main",
        "eb-employees",
        "national-bonds-staff"
    ]
    
    for prefix in custom_prefixes:
        config = {
            "prefix": prefix,
            "expiry_days": 30,
            "max_responses": 500
        }
        
        response = requests.post(f"{BASE_URL}/companies/{company_id}/generate-link",
                               json=config,
                               headers=headers)
        
        if response.status_code == 200:
            link_data = response.json()
            if prefix in link_data['url']:
                print(f"✓ Custom prefix '{prefix}' applied successfully")
            else:
                print(f"✗ Custom prefix '{prefix}' not found in URL: {link_data['url']}")
        else:
            print(f"✗ Failed to apply custom prefix '{prefix}': {response.status_code}")
            print(f"  Response: {response.text}")
    
    return True

def main():
    """Run URL generation and renewal tests."""
    print("=== Company URL Generation and Renewal Test ===\n")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("Cannot proceed without admin authentication")
        return
    
    print("✓ Admin authentication successful\n")
    
    # Test unlimited URL generation
    companies = test_url_generation_unlimited(token)
    if not companies:
        print("Cannot proceed without companies")
        return
    
    # Use first company for detailed testing
    test_company_id = companies[0]['id']
    
    # Test QR code generation
    qr_success = test_qr_code_generation(token, test_company_id)
    
    # Test URL expiration and renewal
    renewal_success = test_url_expiration_and_renewal(token, test_company_id)
    
    # Test custom URL prefixes
    prefix_success = test_custom_url_prefixes(token, test_company_id)
    
    print("\n=== Test Summary ===")
    print(f"Unlimited URL Generation: {'✓' if companies else '✗'}")
    print(f"QR Code Generation: {'✓' if qr_success else '✗'}")
    print(f"URL Expiration & Renewal: {'✓' if renewal_success else '✗'}")
    print(f"Custom URL Prefixes: {'✓' if prefix_success else '✗'}")

if __name__ == "__main__":
    main()