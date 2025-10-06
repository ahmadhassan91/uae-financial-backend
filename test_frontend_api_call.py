#!/usr/bin/env python3
"""
Test the exact API call that the frontend makes.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.localization.service import LocalizationService
from app.models import LocalizedContent
from sqlalchemy import and_


async def test_frontend_api_simulation():
    """Simulate the exact API call the frontend makes."""
    print("=== Testing Frontend API Simulation ===")
    
    db = SessionLocal()
    
    try:
        # Test the exact logic from the API endpoint
        service = LocalizationService(db)
        language = "en"
        
        print(f"Testing for language: {language}")
        
        # Get all available UI content keys for this language (same as API)
        all_ui_content = db.query(LocalizedContent).filter(
            and_(
                LocalizedContent.content_type == "ui",
                LocalizedContent.language == language,
                LocalizedContent.is_active == True
            )
        ).all()
        
        content_keys = [item.content_id for item in all_ui_content]
        print(f"Found {len(content_keys)} content keys for {language}")
        
        # Show first 10 keys
        print("Sample keys:", content_keys[:10])
        
        # Test the service method
        translations = await service.get_ui_content_by_language(content_keys, language)
        print(f"Service returned {len(translations)} translations")
        
        # Test key homepage elements
        homepage_keys = [
            'financial_health_assessment',
            'trusted_uae_institution',
            'transparent_scoring_description',
            'welcome_message',
            'start_survey'
        ]
        
        print(f"\nTesting homepage keys:")
        for key in homepage_keys:
            if key in translations:
                value = translations[key][:50] + "..." if len(translations[key]) > 50 else translations[key]
                print(f"  ✓ {key}: '{value}'")
            else:
                print(f"  ❌ Missing: {key}")
        
        # Test Arabic
        print(f"\n--- Testing Arabic ---")
        language = "ar"
        
        all_ui_content_ar = db.query(LocalizedContent).filter(
            and_(
                LocalizedContent.content_type == "ui",
                LocalizedContent.language == language,
                LocalizedContent.is_active == True
            )
        ).all()
        
        content_keys_ar = [item.content_id for item in all_ui_content_ar]
        print(f"Found {len(content_keys_ar)} Arabic content keys")
        
        translations_ar = await service.get_ui_content_by_language(content_keys_ar, language)
        print(f"Service returned {len(translations_ar)} Arabic translations")
        
        print(f"\nTesting Arabic homepage keys:")
        for key in homepage_keys:
            if key in translations_ar:
                value = translations_ar[key][:50] + "..." if len(translations_ar[key]) > 50 else translations_ar[key]
                print(f"  ✓ {key}: '{value}'")
            else:
                print(f"  ❌ Missing: {key}")
        
        # Test the exact return format
        print(f"\n--- API Response Format Test ---")
        print(f"English response type: {type(translations)}")
        print(f"Arabic response type: {type(translations_ar)}")
        
        if translations:
            sample_key = list(translations.keys())[0]
            print(f"Sample English entry: {sample_key} -> {type(translations[sample_key])}")
        
        if translations_ar:
            sample_key_ar = list(translations_ar.keys())[0]
            print(f"Sample Arabic entry: {sample_key_ar} -> {type(translations_ar[sample_key_ar])}")
        
        print(f"\n✅ API simulation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in API simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_frontend_api_simulation())