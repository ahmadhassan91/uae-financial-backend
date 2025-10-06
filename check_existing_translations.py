#!/usr/bin/env python3
"""
Check existing translations in the database
This script will show what localization data actually exists
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_existing_translations():
    """Check what translations currently exist in the database"""
    print("🔍 Checking Existing Translations in Database")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Check if localized_content table exists
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'localized_content'
        """)
        
        if not cursor.fetchone():
            print("❌ localized_content table does not exist")
            print("💡 Need to run database migrations first")
            return
        
        print("✅ localized_content table exists")
        
        # Get all existing translations
        cursor.execute("""
            SELECT content_type, content_id, language, title, text, is_active, created_at
            FROM localized_content 
            ORDER BY content_type, content_id, language
        """)
        
        translations = cursor.fetchall()
        
        if not translations:
            print("📭 No translations found in database")
            print("💡 Database is empty - need to populate with translations")
            return
        
        print(f"📊 Found {len(translations)} translations in database")
        print("\n" + "=" * 60)
        
        # Group by content type
        by_type = {}
        for trans in translations:
            content_type, content_id, language, title, text, is_active, created_at = trans
            if content_type not in by_type:
                by_type[content_type] = {}
            if content_id not in by_type[content_type]:
                by_type[content_type][content_id] = {}
            by_type[content_type][content_id][language] = {
                'title': title,
                'text': text[:100] + '...' if text and len(text) > 100 else text,
                'is_active': is_active,
                'created_at': created_at
            }
        
        # Display by content type
        for content_type, items in by_type.items():
            print(f"\n📂 {content_type.upper()} ({len(items)} items)")
            print("-" * 40)
            
            for content_id, languages in items.items():
                print(f"  🔑 {content_id}")
                for lang, data in languages.items():
                    status = "✅" if data['is_active'] else "❌"
                    print(f"    {status} {lang}: {data['text']}")
        
        # Summary by language
        print(f"\n📈 SUMMARY BY LANGUAGE")
        print("-" * 30)
        
        lang_counts = {}
        for trans in translations:
            lang = trans[2]
            if lang not in lang_counts:
                lang_counts[lang] = 0
            lang_counts[lang] += 1
        
        for lang, count in lang_counts.items():
            print(f"  {lang}: {count} translations")
        
        cursor.close()
        conn.close()
        
        return by_type
        
    except Exception as e:
        print(f"❌ Error checking translations: {e}")
        return None

def check_survey_questions():
    """Check what survey questions exist that need translation"""
    print(f"\n🔍 Checking Survey Questions That Need Translation")
    print("=" * 60)
    
    try:
        from app.surveys.question_definitions import SURVEY_QUESTIONS_V2
        
        print(f"📊 Found {len(SURVEY_QUESTIONS_V2)} survey questions")
        
        for i, question in enumerate(SURVEY_QUESTIONS_V2[:5], 1):  # Show first 5
            print(f"\n  {i}. Question ID: {question.id}")
            print(f"     Text: {question.text[:80]}...")
            print(f"     Type: {question.type}")
            print(f"     Options: {len(question.options)} options")
        
        if len(SURVEY_QUESTIONS_V2) > 5:
            print(f"\n  ... and {len(SURVEY_QUESTIONS_V2) - 5} more questions")
        
        return SURVEY_QUESTIONS_V2
        
    except Exception as e:
        print(f"❌ Error checking survey questions: {e}")
        return []

def check_frontend_translations():
    """Check what translations the frontend is using"""
    print(f"\n🔍 Checking Frontend Translation Keys")
    print("=" * 60)
    
    try:
        # Read the simple translations file
        with open('frontend/src/lib/simple-translations.ts', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count translation keys
        import re
        
        # Find all translation keys in the file
        key_pattern = r"'([^']+)':"
        keys = re.findall(key_pattern, content)
        
        # Filter out language codes
        translation_keys = [key for key in keys if key not in ['en', 'ar']]
        
        print(f"📊 Found {len(translation_keys)} translation keys in frontend")
        
        # Group by category
        categories = {}
        for key in translation_keys:
            if '_' in key:
                category = key.split('_')[0]
            else:
                category = 'general'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(key)
        
        for category, keys in categories.items():
            print(f"\n  📂 {category}: {len(keys)} keys")
            for key in keys[:3]:  # Show first 3
                print(f"    - {key}")
            if len(keys) > 3:
                print(f"    ... and {len(keys) - 3} more")
        
        return translation_keys
        
    except Exception as e:
        print(f"❌ Error checking frontend translations: {e}")
        return []

def identify_missing_translations(existing_data, frontend_keys, survey_questions):
    """Identify what translations are missing"""
    print(f"\n🔍 Identifying Missing Translations")
    print("=" * 60)
    
    missing = {
        'homepage': [],
        'survey_questions': [],
        'results_page': [],
        'ui_elements': []
    }
    
    # Check homepage translations
    homepage_keys = [key for key in frontend_keys if any(word in key.lower() for word in 
                    ['welcome', 'financial', 'health', 'assessment', 'start', 'begin', 'transparent', 'privacy'])]
    
    if existing_data and 'ui' in existing_data:
        existing_ui_keys = list(existing_data['ui'].keys())
        missing['homepage'] = [key for key in homepage_keys if key not in existing_ui_keys]
    else:
        missing['homepage'] = homepage_keys
    
    # Check survey questions
    if existing_data and 'question' in existing_data:
        existing_question_ids = list(existing_data['question'].keys())
        missing_questions = [q for q in survey_questions if q.id not in existing_question_ids]
        missing['survey_questions'] = [q.id for q in missing_questions]
    else:
        missing['survey_questions'] = [q.id for q in survey_questions]
    
    # Check results page translations
    results_keys = [key for key in frontend_keys if any(word in key.lower() for word in 
                   ['score', 'result', 'recommendation', 'report', 'download', 'excellent', 'good', 'fair'])]
    
    if existing_data and 'ui' in existing_data:
        missing['results_page'] = [key for key in results_keys if key not in existing_data['ui']]
    else:
        missing['results_page'] = results_keys
    
    # Summary
    print("📋 MISSING TRANSLATIONS SUMMARY:")
    print(f"  🏠 Homepage: {len(missing['homepage'])} keys")
    print(f"  📝 Survey Questions: {len(missing['survey_questions'])} questions")
    print(f"  📊 Results Page: {len(missing['results_page'])} keys")
    
    if missing['homepage']:
        print(f"\n  Missing Homepage Keys (first 5):")
        for key in missing['homepage'][:5]:
            print(f"    - {key}")
    
    if missing['survey_questions']:
        print(f"\n  Missing Survey Questions (first 5):")
        for qid in missing['survey_questions'][:5]:
            print(f"    - {qid}")
    
    if missing['results_page']:
        print(f"\n  Missing Results Keys (first 5):")
        for key in missing['results_page'][:5]:
            print(f"    - {key}")
    
    return missing

def main():
    """Main function to check existing translations"""
    print("🚀 Translation Database Analysis")
    print("=" * 60)
    
    # Step 1: Check existing translations in database
    existing_data = check_existing_translations()
    
    # Step 2: Check survey questions
    survey_questions = check_survey_questions()
    
    # Step 3: Check frontend translation keys
    frontend_keys = check_frontend_translations()
    
    # Step 4: Identify missing translations
    missing = identify_missing_translations(existing_data, frontend_keys, survey_questions)
    
    print(f"\n" + "=" * 60)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 60)
    
    if existing_data:
        print("✅ Database has existing translations")
        print("💡 Need to add missing translations for complete coverage")
    else:
        print("📭 Database is empty")
        print("💡 Need to populate all translations from scratch")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Add missing homepage translations")
    print("2. Add all survey question translations")
    print("3. Add results page translations")
    print("4. Test frontend integration")

if __name__ == "__main__":
    main()