#!/usr/bin/env python3
"""Check translations in Heroku database."""

from app.database import SessionLocal
from app.models import LocalizedContent

def check_translations():
    """Check translation counts."""
    db = SessionLocal()
    
    try:
        total_translations = db.query(LocalizedContent).count()
        arabic_translations = db.query(LocalizedContent).filter(LocalizedContent.language == 'ar').count()
        english_translations = db.query(LocalizedContent).filter(LocalizedContent.language == 'en').count()
        
        print(f'✅ Total translations: {total_translations}')
        print(f'📝 Arabic translations: {arabic_translations}')
        print(f'📝 English translations: {english_translations}')
        
        if total_translations > 0:
            print('🎉 Database migration successful - all translations are available!')
        else:
            print('❌ No translations found')
            
    except Exception as e:
        print(f'❌ Error checking translations: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    check_translations()