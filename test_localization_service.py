"""Test the localization service functionality."""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.localization.service import LocalizationService
from app.models import LocalizedContent


async def test_localization_service():
    """Test the localization service functionality."""
    print("Testing Localization Service...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create localization service
        service = LocalizationService(db)
        
        # Test 1: Create localized content
        print("\n1. Testing content creation...")
        
        test_content = await service.create_localized_content(
            content_type="question",
            content_id="test_question",
            language="ar",
            text="هذا سؤال تجريبي؟",
            title="سؤال تجريبي",
            options=[
                {"value": 1, "label": "نعم"},
                {"value": 2, "label": "لا"}
            ]
        )
        
        print(f"✓ Created content with ID: {test_content.id}")
        
        # Test 2: Get questions by language
        print("\n2. Testing questions retrieval...")
        
        questions = await service.get_questions_by_language("en")
        print(f"✓ Retrieved {len(questions)} English questions")
        
        # Test 3: Get UI translations
        print("\n3. Testing UI translations...")
        
        ui_keys = ["welcome_message", "start_survey", "next_question"]
        translations = await service.get_ui_content_by_language(ui_keys, "en")
        print(f"✓ Retrieved {len(translations)} UI translations")
        
        # Test 4: Content validation
        print("\n4. Testing content validation...")
        
        validation = await service.validate_content(
            "question", "test_q", "ar", "هذا سؤال صحيح؟"
        )
        print(f"✓ Validation result: {validation['is_valid']}")
        
        # Test 5: Demographic filtering
        print("\n5. Testing demographic filtering...")
        
        demographic_profile = {
            "nationality": "UAE",
            "age": 30,
            "emirate": "Dubai"
        }
        
        filtered_questions = await service.get_questions_by_language(
            "en", demographic_profile
        )
        print(f"✓ Retrieved {len(filtered_questions)} filtered questions")
        
        # Test 6: Get supported languages
        print("\n6. Testing supported languages...")
        
        languages = await service.get_supported_languages()
        print(f"✓ Supported languages: {[lang['code'] for lang in languages]}")
        
        # Test 7: Update content
        print("\n7. Testing content update...")
        
        updated_content = await service.update_localized_content(
            test_content.id,
            text="هذا سؤال محدث؟",
            title="سؤال محدث"
        )
        
        if updated_content:
            print(f"✓ Updated content: {updated_content.text}")
        
        # Test 8: Get content for approval
        print("\n8. Testing content approval workflow...")
        
        approval_content = await service.get_content_for_approval("ar", "question")
        print(f"✓ Found {len(approval_content)} items for approval")
        
        print("\n🎉 All localization service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test data
        try:
            db.query(LocalizedContent).filter(
                LocalizedContent.content_id == "test_question"
            ).delete()
            db.commit()
            print("✓ Cleaned up test data")
        except:
            pass
        
        db.close()


async def test_arabic_content_rendering():
    """Test Arabic content rendering and RTL support."""
    print("\nTesting Arabic Content Rendering...")
    
    db = SessionLocal()
    
    try:
        service = LocalizationService(db)
        
        # Create sample Arabic content
        arabic_question = await service.create_localized_content(
            content_type="question",
            content_id="arabic_test",
            language="ar",
            text="ما هو مستوى دخلك الشهري؟",
            options=[
                {"value": 1, "label": "أقل من 5000 درهم"},
                {"value": 2, "label": "5000-10000 درهم"},
                {"value": 3, "label": "10000-20000 درهم"},
                {"value": 4, "label": "أكثر من 20000 درهم"}
            ]
        )
        
        print(f"✓ Created Arabic question: {arabic_question.text}")
        
        # Test Arabic character detection
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in arabic_question.text)
        print(f"✓ Contains Arabic characters: {has_arabic}")
        
        # Test recommendations with cultural adaptations
        sample_recommendations = [
            {
                "id": "savings_basic",
                "category": "savings",
                "title": "Basic Savings",
                "description": "Start saving money regularly"
            }
        ]
        
        demographic_profile = {
            "nationality": "UAE",
            "islamic_finance_preference": True
        }
        
        localized_recs = await service.get_recommendations_by_language(
            sample_recommendations, "ar", demographic_profile
        )
        
        print(f"✓ Processed {len(localized_recs)} recommendations with cultural adaptations")
        
        # Clean up
        db.query(LocalizedContent).filter(
            LocalizedContent.content_id == "arabic_test"
        ).delete()
        db.commit()
        
        print("✓ Arabic content rendering tests passed!")
        
    except Exception as e:
        print(f"❌ Arabic content test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


async def main():
    """Run all localization tests."""
    print("=== Localization Service Tests ===")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    await test_localization_service()
    await test_arabic_content_rendering()
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(main())