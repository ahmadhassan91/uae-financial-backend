#!/usr/bin/env python3
"""
Test the localization API endpoints to ensure they're working correctly.
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


def test_api_endpoints():
    """Test the localization API endpoints."""
    print("=== Testing Localization API Endpoints ===")
    
    # Test database content first
    db = SessionLocal()
    try:
        # Check English content
        en_ui_count = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "ui",
            LocalizedContent.language == "en",
            LocalizedContent.is_active == True
        ).count()
        
        # Check Arabic content
        ar_ui_count = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "ui",
            LocalizedContent.language == "ar",
            LocalizedContent.is_active == True
        ).count()
        
        print(f"Database content:")
        print(f"  English UI items: {en_ui_count}")
        print(f"  Arabic UI items: {ar_ui_count}")
        
        # Show sample content
        sample_en = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "ui",
            LocalizedContent.language == "en",
            LocalizedContent.content_id == "financial_health_assessment"
        ).first()
        
        sample_ar = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "ui",
            LocalizedContent.language == "ar",
            LocalizedContent.content_id == "financial_health_assessment"
        ).first()
        
        if sample_en:
            print(f"  Sample EN: {sample_en.content_id} = '{sample_en.text}'")
        else:
            print(f"  ❌ Missing English 'financial_health_assessment'")
            
        if sample_ar:
            print(f"  Sample AR: {sample_ar.content_id} = '{sample_ar.text}'")
        else:
            print(f"  ❌ Missing Arabic 'financial_health_assessment'")
        
    finally:
        db.close()
    
    # Test API endpoints (assuming server is running on localhost:8000)
    base_url = "http://localhost:8000"
    
    print(f"\nTesting API endpoints at {base_url}:")
    
    # Test English translations
    try:
        response = requests.get(f"{base_url}/api/localization/ui/en", timeout=5)
        if response.status_code == 200:
            en_translations = response.json()
            print(f"  ✓ English API: {len(en_translations)} translations")
            
            # Check for key translations
            key_checks = ['financial_health_assessment', 'welcome_message', 'start_survey']
            for key in key_checks:
                if key in en_translations:
                    print(f"    ✓ {key}: '{en_translations[key][:50]}...'")
                else:
                    print(f"    ❌ Missing key: {key}")
        else:
            print(f"  ❌ English API failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ English API error: {str(e)}")
    
    # Test Arabic translations
    try:
        response = requests.get(f"{base_url}/api/localization/ui/ar", timeout=5)
        if response.status_code == 200:
            ar_translations = response.json()
            print(f"  ✓ Arabic API: {len(ar_translations)} translations")
            
            # Check for key translations
            key_checks = ['financial_health_assessment', 'welcome_message', 'start_survey']
            for key in key_checks:
                if key in ar_translations:
                    print(f"    ✓ {key}: '{ar_translations[key][:50]}...'")
                else:
                    print(f"    ❌ Missing key: {key}")
        else:
            print(f"  ❌ Arabic API failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Arabic API error: {str(e)}")
    
    print(f"\n📋 Troubleshooting:")
    print(f"1. Make sure your backend server is running")
    print(f"2. Check that the API routes are registered")
    print(f"3. Verify database has content populated")
    print(f"4. Test the frontend API calls in browser dev tools")


if __name__ == "__main__":
    test_api_endpoints()