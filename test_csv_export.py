#!/usr/bin/env python3
"""
Simple test for CSV export functionality.
"""

import requests

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
    
    print("Testing CSV export...")
    
    response = requests.get(f"{BASE_URL}/companies/export-csv", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"Content length: {len(response.content)}")
        print(f"First 200 chars: {response.content[:200]}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    main()