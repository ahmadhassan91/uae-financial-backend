#!/usr/bin/env python3
"""
Test admin authentication and API access.
"""
import asyncio
import sys
import os
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User


def test_admin_authentication():
    """Test admin authentication flow."""
    print("=== Testing Admin Authentication ===")
    
    # Check if admin user exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(
            User.is_admin == True,
            User.is_active == True
        ).first()
        
        if not admin_user:
            print("❌ No admin user found in database!")
            print("   Run: python create_admin_user.py")
            return
        
        print(f"✓ Admin user found: {admin_user.email}")
        
    finally:
        db.close()
    
    # Test login
    base_url = "http://localhost:8000"
    
    print(f"\nTesting admin login at {base_url}:")
    
    try:
        # Test login with the correct credentials
        login_response = requests.post(f"{base_url}/auth/login", 
            json={
                "email": "admin@nationalbonds.ae",
                "password": "admin123"
            },
            timeout=5
        )
        
        print(f"  Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print(f"  ✓ Login successful, got token")
                
                # Test admin API with token
                headers = {'Authorization': f'Bearer {access_token}'}
                
                admin_response = requests.get(
                    f"{base_url}/api/admin/localized-content",
                    headers=headers,
                    timeout=5
                )
                
                print(f"  Admin API status: {admin_response.status_code}")
                
                if admin_response.status_code == 200:
                    data = admin_response.json()
                    content_count = len(data.get('content', []))
                    print(f"  ✓ Admin API working: {content_count} content items")
                    
                    return True
                else:
                    print(f"  ❌ Admin API failed: {admin_response.text[:200]}")
            else:
                print(f"  ❌ No access token in response")
        else:
            print(f"  ❌ Login failed: {login_response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Authentication test error: {str(e)}")
    
    return False


def print_troubleshooting_guide():
    """Print troubleshooting steps."""
    print(f"\n📋 Troubleshooting Guide:")
    print(f"1. Make sure backend server is running: uvicorn app.main:app --reload")
    print(f"2. Create admin user if needed: python create_admin_user.py")
    print(f"3. Check admin user credentials in database")
    print(f"4. Verify admin routes are working: python test_admin_routes_direct.py")
    print(f"5. Test frontend authentication in browser")


if __name__ == "__main__":
    success = test_admin_authentication()
    
    if not success:
        print_troubleshooting_guide()
    else:
        print(f"\n✅ Admin authentication is working correctly!")
        print(f"   The frontend should now be able to load admin content.")