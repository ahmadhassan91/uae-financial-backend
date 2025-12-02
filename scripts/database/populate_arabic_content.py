"""Script to populate the database with sample Arabic content."""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.localization.service import LocalizationService
from app.localization.sample_data import (
    get_sample_arabic_questions,
    get_sample_arabic_ui,
    get_sample_arabic_recommendations
)


async def populate_arabic_questions(db: Session, service: LocalizationService):
    """Populate Arabic question translations."""
    print("Populating Arabic questions...")
    
    questions = get_sample_arabic_questions()
    success_count = 0
    
    for question_id, question_data in questions.items():
        try:
            await service.create_localized_content(
                content_type="question",
                content_id=question_id,
                language="ar",
                text=question_data["text"],
                options=question_data["options"]
            )
            success_count += 1
            print(f"✓ Added Arabic translation for {question_id}")
            
        except Exception as e:
            print(f"✗ Error adding {question_id}: {str(e)}")
    
    print(f"Successfully added {success_count}/{len(questions)} Arabic questions")


async def populate_arabic_ui(db: Session, service: LocalizationService):
    """Populate Arabic UI translations."""
    print("\nPopulating Arabic UI translations...")
    
    ui_translations = get_sample_arabic_ui()
    success_count = 0
    
    for ui_key, translation in ui_translations.items():
        try:
            await service.create_localized_content(
                content_type="ui",
                content_id=ui_key,
                language="ar",
                text=translation
            )
            success_count += 1
            print(f"✓ Added Arabic UI translation for {ui_key}")
            
        except Exception as e:
            print(f"✗ Error adding UI translation {ui_key}: {str(e)}")
    
    print(f"Successfully added {success_count}/{len(ui_translations)} Arabic UI translations")


async def populate_arabic_recommendations(db: Session, service: LocalizationService):
    """Populate Arabic recommendation translations."""
    print("\nPopulating Arabic recommendations...")
    
    recommendations = get_sample_arabic_recommendations()
    success_count = 0
    
    for rec_id, rec_data in recommendations.items():
        try:
            await service.create_localized_content(
                content_type="recommendation",
                content_id=rec_id,
                language="ar",
                text=rec_data["text"],
                title=rec_data["title"],
                extra_data=rec_data.get("extra_data")
            )
            success_count += 1
            print(f"✓ Added Arabic recommendation for {rec_id}")
            
        except Exception as e:
            print(f"✗ Error adding recommendation {rec_id}: {str(e)}")
    
    print(f"Successfully added {success_count}/{len(recommendations)} Arabic recommendations")


async def main():
    """Main function to populate all Arabic content."""
    print("Starting Arabic content population...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create localization service
        service = LocalizationService(db)
        
        # Populate different types of content
        await populate_arabic_questions(db, service)
        await populate_arabic_ui(db, service)
        await populate_arabic_recommendations(db, service)
        
        print("\n🎉 Arabic content population completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {str(e)}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())