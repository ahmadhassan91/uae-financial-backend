#!/usr/bin/env python3
"""
Test script for company question management functionality.
Tests the enhanced question set management features.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, CompanyTracker, CompanyQuestionSet, QuestionVariation
from app.companies.question_manager import CompanyQuestionManager
from app.surveys.question_definitions import SURVEY_QUESTIONS_V2
import json

# Test database
TEST_DB_URL = "sqlite:///./test_company_questions.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_test_db():
    """Set up test database with sample data."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create test admin user
        admin_user = User(
            email="admin@test.com",
            username="admin",
            hashed_password="hashed_password",
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        
        # Create test company
        company = CompanyTracker(
            company_name="Test Company Inc",
            company_email="test@company.com",
            contact_person="John Doe",
            unique_url="test-company",
            is_active=True
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create some question variations
        variations = [
            QuestionVariation(
                base_question_id="q1_income_stability",
                variation_name="uae_citizen_version",
                language="en",
                text="My income from UAE-based employment is stable and predictable each month.",
                options=[
                    {"value": 5, "label": "Strongly Agree"},
                    {"value": 4, "label": "Agree"},
                    {"value": 3, "label": "Neutral"},
                    {"value": 2, "label": "Disagree"},
                    {"value": 1, "label": "Strongly Disagree"}
                ],
                factor="income_stream",
                weight=10
            ),
            QuestionVariation(
                base_question_id="q2_income_sources",
                variation_name="expat_version",
                language="en",
                text="I have multiple income sources including remittances or international investments.",
                options=[
                    {"value": 5, "label": "Multiple international streams"},
                    {"value": 4, "label": "Local + international income"},
                    {"value": 3, "label": "Consistent side income"},
                    {"value": 2, "label": "Occasional additional income"},
                    {"value": 1, "label": "Single salary only"}
                ],
                factor="income_stream",
                weight=10
            )
        ]
        
        for variation in variations:
            db.add(variation)
        
        db.commit()
        return company.id
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def test_question_set_creation():
    """Test creating a custom question set."""
    print("Testing question set creation...")
    
    db = TestingSessionLocal()
    manager = CompanyQuestionManager(db)
    
    try:
        company_id = 1  # From setup
        
        # Get first 5 questions for testing
        base_questions = [q.id for q in SURVEY_QUESTIONS_V2[:5]]
        
        question_set = await manager.create_custom_question_set(
            company_id=company_id,
            name="Test Question Set",
            description="A test question set for company",
            base_questions=base_questions,
            question_variations={
                "q1_income_stability": "uae_citizen_version",
                "q2_income_sources": "expat_version"
            }
        )
        
        print(f"✓ Created question set: {question_set.name}")
        print(f"  - ID: {question_set.id}")
        print(f"  - Base questions: {len(question_set.base_questions)}")
        print(f"  - Variations: {len(question_set.question_variations or {})}")
        
        return question_set.id
        
    except Exception as e:
        print(f"✗ Error creating question set: {e}")
        return None
    finally:
        db.close()

async def test_question_set_retrieval():
    """Test retrieving question set for company URL."""
    print("\nTesting question set retrieval...")
    
    db = TestingSessionLocal()
    manager = CompanyQuestionManager(db)
    
    try:
        # Test with company URL
        question_set = await manager.get_company_question_set(
            company_url="test-company",
            language="en"
        )
        
        print(f"✓ Retrieved question set for company URL")
        print(f"  - Question set ID: {question_set['question_set_id']}")
        print(f"  - Total questions: {question_set['metadata']['total_questions']}")
        print(f"  - Company config: {question_set['company_config'] is not None}")
        
        # Test with non-existent company URL (should return default)
        default_set = await manager.get_company_question_set(
            company_url="non-existent-company",
            language="en"
        )
        
        print(f"✓ Retrieved default question set for non-existent company")
        print(f"  - Question set ID: {default_set['question_set_id']}")
        print(f"  - Total questions: {default_set['metadata']['total_questions']}")
        
    except Exception as e:
        print(f"✗ Error retrieving question set: {e}")
    finally:
        db.close()

async def test_question_set_analytics():
    """Test question set analytics."""
    print("\nTesting question set analytics...")
    
    db = TestingSessionLocal()
    manager = CompanyQuestionManager(db)
    
    try:
        company_id = 1
        
        analytics = await manager.get_question_set_analytics(company_id)
        
        print(f"✓ Retrieved analytics for company")
        print(f"  - Total responses: {analytics['total_responses']}")
        print(f"  - Average score: {analytics['average_score']}")
        print(f"  - Question performance entries: {len(analytics['question_performance'])}")
        print(f"  - Demographic breakdown entries: {len(analytics['demographic_breakdown'])}")
        
    except Exception as e:
        print(f"✗ Error retrieving analytics: {e}")
    finally:
        db.close()

async def test_question_set_versioning():
    """Test question set versioning."""
    print("\nTesting question set versioning...")
    
    db = TestingSessionLocal()
    manager = CompanyQuestionManager(db)
    
    try:
        company_id = 1
        question_set_id = 1  # From creation test
        
        # Update question set (creates new version)
        updated_set = await manager.update_question_set(
            question_set_id,
            name="Updated Test Question Set",
            description="Updated description",
            base_questions=[q.id for q in SURVEY_QUESTIONS_V2[:3]]  # Fewer questions
        )
        
        print(f"✓ Updated question set (created new version)")
        print(f"  - New version ID: {updated_set.id}")
        print(f"  - Name: {updated_set.name}")
        print(f"  - Base questions: {len(updated_set.base_questions)}")
        
        # Get all versions
        versions = await manager.get_question_set_versions(company_id)
        print(f"✓ Retrieved {len(versions)} versions")
        
        for i, version in enumerate(versions):
            print(f"  - Version {i+1}: {version.name} ({'Active' if version.is_active else 'Inactive'})")
        
    except Exception as e:
        print(f"✗ Error with versioning: {e}")
    finally:
        db.close()

async def main():
    """Run all tests."""
    print("=== Company Question Management Tests ===\n")
    
    # Setup
    print("Setting up test database...")
    company_id = setup_test_db()
    print(f"✓ Test database setup complete. Company ID: {company_id}\n")
    
    # Run tests
    question_set_id = await test_question_set_creation()
    if question_set_id:
        await test_question_set_retrieval()
        await test_question_set_analytics()
        await test_question_set_versioning()
    
    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    asyncio.run(main())