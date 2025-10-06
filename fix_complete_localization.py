#!/usr/bin/env python3
"""Complete localization fix - add all missing translations."""

import asyncio
from app.database import get_db
from app.localization.service import LocalizationService

async def fix_complete_localization():
    """Add all missing translations to fix homepage and results page."""
    db = next(get_db())
    service = LocalizationService(db)
    
    try:
        print("🔧 Starting complete localization fix...")
        
        # Import and run the homepage translations
        from add_missing_homepage_translations import HOMEPAGE_TRANSLATIONS, RESULTS_TRANSLATIONS, ADDITIONAL_UI_TRANSLATIONS
        from add_missing_english_translations import ENGLISH_TRANSLATIONS
        
        # Combine all Arabic translations
        all_arabic = {
            **HOMEPAGE_TRANSLATIONS,
            **RESULTS_TRANSLATIONS,
            **ADDITIONAL_UI_TRANSLATIONS
        }
        
        print(f"📝 Adding {len(all_arabic)} Arabic translations...")
        arabic_added = 0
        
        for key, text in all_arabic.items():
            try:
                await service.create_localized_content(
                    content_type="ui",
                    content_id=key,
                    language="ar",
                    text=text,
                    version="1.0"
                )
                arabic_added += 1
                print(f"✅ AR: {key}")
            except Exception as e:
                print(f"❌ AR {key}: {str(e)}")
        
        print(f"📝 Adding {len(ENGLISH_TRANSLATIONS)} English translations...")
        english_added = 0
        
        for key, text in ENGLISH_TRANSLATIONS.items():
            try:
                await service.create_localized_content(
                    content_type="ui",
                    content_id=key,
                    language="en",
                    text=text,
                    version="1.0"
                )
                english_added += 1
                print(f"✅ EN: {key}")
            except Exception as e:
                print(f"❌ EN {key}: {str(e)}")
        
        print(f"\n🎉 LOCALIZATION FIX COMPLETE!")
        print(f"Arabic translations added: {arabic_added}")
        print(f"English translations added: {english_added}")
        print(f"Total translations processed: {arabic_added + english_added}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fix_complete_localization())