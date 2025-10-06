#!/usr/bin/env python3
"""
Test the admin API endpoints to ensure they're working correctly.
"""
import asyncio
import sys
import os
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import LocalizedContent


def test_admin_api_endpoints():
    """Test the admin API endpoints."""
    print("=== Testing Admin API Endpoints ===")
    
    # Test database content first
    db = SessionLocal()
    try:
        # Check content in database
        total_content = db.query(LocalizedContent).count()
        en_content = db.query(LocalizedContent).filter(
            LocalizedContent.language == "en"
        ).count()
        ar_content = db.query(LocalizedContent).filter(
            LocalizedContent.language == "ar"
        ).count()
        
        print(f"Database content:")
        print(f"  Total content items: {total_content}")
        print(f"  English content: {en_content}")
        print(f"  Arabic content: {ar_content}")
        
    finally:
        db.close()
    
    # Test admin API endpoints (assuming server is running on localhost:8000)
    base_url = "http://localhost:8000"
    
    print(f"\nTesting admin API endpoints at {base_url}:")
    
    # Test admin localized content endpoint (without auth for now)
    try:
        # Test the direct backend URL (not through Next.js proxy)
        response = requests.get(f"{base_url}/api/admin/localized-content", timeout=5)
        print(f"  Admin API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Admin API working: {len(data.get('content', []))} items returned")
        elif response.status_code == 401:
            print(f"  ⚠️  Admin API requires authentication (expected)")
        elif response.status_code == 404:
            print(f"  ❌ Admin API not found - route issue")
        else:
            print(f"  ❌ Admin API error: {response.status_code}")
            print(f"      Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Admin API error: {str(e)}")
    
    # Test through Next.js proxy
    try:
        response = requests.get(f"http://localhost:3000/api/admin/localized-content", timeout=5)
        print(f"  Next.js proxy status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Next.js proxy working: {len(data.get('content', []))} items")
        elif response.status_code == 401:
            print(f"  ⚠️  Next.js proxy requires authentication (expected)")
        elif response.status_code == 404:
            print(f"  ❌ Next.js proxy not found")
        else:
            print(f"  ❌ Next.js proxy error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Next.js proxy error: {str(e)}")
    
    print(f"\n📋 Troubleshooting:")
    print(f"1. Make sure backend server is running on port 8000")
    print(f"2. Make sure Next.js dev server is running on port 3000")
    print(f"3. Check that admin routes have /api prefix")
    print(f"4. Verify authentication is working")


if __name__ == "__main__":
    test_admin_api_endpoints()