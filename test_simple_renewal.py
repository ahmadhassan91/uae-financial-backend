#!/usr/bin/env python3
"""
Simple test for URL renewal functionality.
"""

import requests
import json
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

def main():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test company
    company_data = {
        "company_name": "Renewal Test Company",
        "company_email": "test@renewal.ae",
        "contact_person": "Test Person"
    }
    
    response = requests.post(f"{BASE_URL}/companies/", json=company_data, headers=headers)
    company = response.json()
    company_id = company['id']
    
    print(f"Created company: {company['company_name']} (ID: {company_id})")
    
    # Generate link with 0 days expiry (should be expired)
    config = {"expiry_days": 0, "max_responses": 100}
    response = requests.post(f"{BASE_URL}/companies/{company_id}/generate-link", 
                           json=config, headers=headers)
    
    if response.status_code == 200:
        link_data = response.json()
        print(f"Generated expired link: {link_data['expires_at']}")
    else:
        print(f"Failed to generate link: {response.text}")
        return
    
    # Check link status
    response = requests.get(f"{BASE_URL}/companies/{company_id}/link-status", headers=headers)
    if response.status_code == 200:
        status = response.json()
        print(f"Link status - Active: {status['has_active_link']}, Expired: {status['is_expired']}")
    
    # Try to renew
    renewal_config = {"expiry_days": 30, "max_responses": 1000}
    response = requests.post(f"{BASE_URL}/companies/{company_id}/renew-link", 
                           json=renewal_config, headers=headers)
    
    if response.status_code == 200:
        renewed = response.json()
        print(f"✓ Link renewed successfully: {renewed['expires_at']}")
    else:
        print(f"✗ Renewal failed: {response.text}")

if __name__ == "__main__":
    main()