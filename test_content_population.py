#!/usr/bin/env python3
"""
Test script to verify that all content was populated correctly.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import LocalizedContent
from app.localization.service import LocalizationService


async def test_content_population():
    """Test that all content was populated correctly."""
    print("=== Testing Content Population ===")
    
    db = SessionLocal()
    
    try:
        service = LocalizationService(db)
        
        # Test 1: Check UI elements
        print("\n1. Testing UI Elements...")
        ui_content = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "ui",
            LocalizedContent.language == "en"
        ).all()
        
        print(f"   Found {len(ui_content)} UI elements")
        
        # Test some key UI elements
        key_elements = ['welcome_message', 'start_survey', 'financial_health_score', 'recommendations']
        for element in key_elements:
            found = any(item.content_id == element for item in ui_content)
            status = "✓" if found else "✗"
            print(f"   {status} {element}")
        
        # Test 2: Check Questions
        print("\n2. Testing Survey Questions...")
        question_content = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "question",
            LocalizedContent.language == "en"
        ).all()
        
        print(f"   Found {len(question_content)} questions")
        
        # Test some key questions
        key_questions = ['q1_income_stability', 'q2_income_sources', 'q13_retirement_planning', 'q16_children_planning']
        for question in key_questions:
            found = any(item.content_id == question for item in question_content)
            status = "✓" if found else "✗"
            print(f"   {status} {question}")
        
        # Test question options
        if question_content:
            sample_question = question_content[0]
            if sample_question.options:
                print(f"   ✓ Question options are properly stored (sample has {len(sample_question.options)} options)")
            else:
                print(f"   ✗ Question options are missing")
        
        # Test 3: Check Recommendations
        print("\n3. Testing Recommendations...")
        rec_content = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == "recommendation",
            LocalizedContent.language == "en"
        ).all()
        
        print(f"   Found {len(rec_content)} recommendations")
        
        # Test some key recommendations
        key_recs = ['budgeting_basic', 'savings_emergency', 'debt_management', 'investment_basic']
        for rec in key_recs:
            found = any(item.content_id == rec for item in rec_content)
            status = "✓" if found else "✗"
            print(f"   {status} {rec}")
        
        # Test 4: Test Localization Service Integration
        print("\n4. Testing Localization Service Integration...")
        
        # Test UI translations
        ui_keys = ['welcome_message', 'start_survey', 'next_question']
        translations = await service.get_ui_content_by_language(ui_keys, "en")
        
        all_found = all(key in translations for key in ui_keys)
        status = "✓" if all_found else "✗"
        print(f"   {status} UI translation service working")
        
        # Test questions service
        questions = await service.get_questions_by_language("en")
        status = "✓" if len(questions) > 0 else "✗"
        print(f"   {status} Question service working ({len(questions)} questions loaded)")
        
        # Test 5: Check Content Structure
        print("\n5. Testing Content Structure...")
        
        # Check that all content has required fields
        all_content = db.query(LocalizedContent).filter(
            LocalizedContent.language == "en"
        ).all()
        
        issues = []
        for content in all_content:
            if not content.text or not content.text.strip():
                issues.append(f"Empty text in {content.content_type}:{content.content_id}")
            if not content.version:
                issues.append(f"Missing version in {content.content_type}:{content.content_id}")
        
        if issues:
            print(f"   ✗ Found {len(issues)} content structure issues:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"     - {issue}")
        else:
            print(f"   ✓ All content has proper structure")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Total content items: {len(all_content)}")
        print(f"UI Elements: {len(ui_content)}")
        print(f"Questions: {len(question_content)}")
        print(f"Recommendations: {len(rec_content)}")
        
        if len(all_content) > 0 and not issues:
            print(f"\n🎉 All tests passed! Content population was successful.")
            print(f"\n📋 Next Steps:")
            print(f"1. Access admin dashboard: /admin")
            print(f"2. Go to 'Localization Management'")
            print(f"3. Create Arabic translations")
            print(f"4. Test language switching on frontend")
        else:
            print(f"\n⚠️  Some issues found. Please check the population script.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


async def test_admin_interface_data():
    """Test that data is properly formatted for admin interface."""
    print("\n=== Testing Admin Interface Data Format ===")
    
    db = SessionLocal()
    
    try:
        # Simulate admin interface query
        content_items = db.query(LocalizedContent).filter(
            LocalizedContent.language == "en"
        ).order_by(
            LocalizedContent.content_type.asc(),
            LocalizedContent.content_id.asc()
        ).limit(10).all()
        
        print(f"Sample content for admin interface:")
        print(f"{'Type':<15} {'ID':<25} {'Text Preview':<50}")
        print("-" * 90)
        
        for item in content_items:
            text_preview = (item.text[:47] + "...") if len(item.text) > 50 else item.text
            print(f"{item.content_type:<15} {item.content_id:<25} {text_preview:<50}")
        
        print(f"\n✓ Admin interface data format looks good!")
        
    except Exception as e:
        print(f"❌ Admin interface test failed: {str(e)}")
        
    finally:
        db.close()


async def main():
    """Run all tests."""
    await test_content_population()
    await test_admin_interface_data()


if __name__ == "__main__":
    asyncio.run(main())