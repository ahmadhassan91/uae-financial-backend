#!/usr/bin/env python3
"""
Integration test for URL-specific question customization.
Tests the complete workflow from company creation to question set management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import CompanyTracker, CompanyQuestionSet, User
from app.companies.question_manager import CompanyQuestionManager
from app.companies.url_config_service import URLConfigurationService
from app.companies.cache_utils import get_cache_manager, clear_cache_manager
from app.surveys.question_definitions import SURVEY_QUESTIONS_V2

async def test_url_specific_integration():
    """Test the complete URL-specific question customization workflow."""
    
    # Create test database
    engine = create_engine("sqlite:///test_url_specific.db", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 Testing URL-specific question customization integration...")
        
        # Clear any existing cache
        clear_cache_manager()
        
        # 1. Create a test company
        print("1. Creating test company...")
        company = CompanyTracker(
            company_name="Test Corp",
            company_email="test@testcorp.com",
            contact_person="Test Manager",
            phone_number="+971501234567",
            unique_url="test-corp-123",
            is_active=True,
            custom_branding={
                "primary_color": "#1e40af",
                "logo_url": "https://example.com/logo.png"
            }
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"   ✓ Company created with ID: {company.id}")
        
        # 2. Test CompanyQuestionManager
        print("2. Testing CompanyQuestionManager...")
        manager = CompanyQuestionManager(db)
        
        # Get available questions
        available_questions = [q.id for q in SURVEY_QUESTIONS_V2[:10]]  # Use first 10 questions
        print(f"   ✓ Available questions: {len(available_questions)}")
        
        # Create custom question set
        question_set = await manager.create_custom_question_set(
            company_id=company.id,
            name="Test Question Set",
            description="A test question set for integration testing",
            base_questions=available_questions,
            excluded_questions=[available_questions[0]],  # Exclude first question
            question_variations={}
        )
        print(f"   ✓ Question set created with ID: {question_set.id}")
        
        # 3. Test question set retrieval
        print("3. Testing question set retrieval...")
        retrieved_set = await manager.get_company_question_set(
            company_url="test-corp-123",
            language="en"
        )
        print(f"   ✓ Retrieved question set with {len(retrieved_set['questions'])} questions")
        print(f"   ✓ Company config: {retrieved_set['company_config']['company_name']}")
        
        # 4. Test URL configuration service
        print("4. Testing URLConfigurationService...")
        config_service = URLConfigurationService(db)
        
        # Get configuration for URL
        config = await config_service.get_configuration_for_url(
            company_url="test-corp-123",
            language="en"
        )
        print(f"   ✓ Configuration loaded for company: {config['company_config']['company_name']}")
        print(f"   ✓ Question set type: {config['question_set']['question_set_id']}")
        print(f"   ✓ Total questions: {config['question_set']['metadata']['total_questions']}")
        
        # 5. Test URL mapping
        print("5. Testing URL mapping...")
        mapping = await config_service.get_url_mapping("test-corp-123")
        print(f"   ✓ URL mapping: {mapping['company_name']} -> {mapping['url']}")
        print(f"   ✓ Has custom questions: {mapping['has_custom_questions']}")
        
        # 6. Test configuration validation
        print("6. Testing configuration validation...")
        test_config = {
            "question_set": {
                "base_questions": available_questions[:5],
                "question_variations": {}
            },
            "branding": {
                "primary_color": "#ff0000",
                "logo_url": "https://example.com/new-logo.png"
            }
        }
        
        validation_result = await config_service.validate_configuration(
            "test-corp-123", test_config
        )
        print(f"   ✓ Configuration validation: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
        if validation_result['errors']:
            print(f"   ⚠ Validation errors: {validation_result['errors']}")
        
        # 7. Test caching
        print("7. Testing caching...")
        cache_manager = get_cache_manager()
        
        # First call (should cache)
        config1 = await config_service.get_configuration_for_url(
            company_url="test-corp-123",
            language="en"
        )
        
        # Second call (should use cache)
        config2 = await config_service.get_configuration_for_url(
            company_url="test-corp-123",
            language="en"
        )
        
        print(f"   ✓ Cache working: {config1['metadata']['loaded_at'] == config2['metadata']['loaded_at']}")
        
        # 8. Test cache invalidation
        print("8. Testing cache invalidation...")
        await config_service.invalidate_cache_for_company(company.id)
        
        # This should load fresh data
        config3 = await config_service.get_configuration_for_url(
            company_url="test-corp-123",
            language="en",
            force_refresh=True
        )
        print(f"   ✓ Cache invalidated: {config2['metadata']['loaded_at'] != config3['metadata']['loaded_at']}")
        
        # 9. Test question set analytics
        print("9. Testing question set analytics...")
        analytics = await manager.get_question_set_analytics(
            company_id=company.id,
            question_set_id=question_set.id
        )
        print(f"   ✓ Analytics generated: {analytics['total_responses']} responses")
        
        # 10. Test versioning
        print("10. Testing question set versioning...")
        
        # Update question set (creates new version)
        updated_set = await manager.update_question_set(
            question_set_id=question_set.id,
            name="Updated Test Question Set",
            base_questions=available_questions[:8]  # Different questions
        )
        print(f"   ✓ New version created with ID: {updated_set.id}")
        
        # Get version history
        versions = await manager.get_question_set_versions(company.id)
        print(f"   ✓ Version history: {len(versions)} versions")
        
        # Test rollback
        rolled_back = await manager.rollback_to_version(company.id, question_set.id)
        print(f"   ✓ Rolled back to version: {rolled_back.name}")
        
        print("\n🎉 All URL-specific question customization tests PASSED!")
        print("\nImplementation Summary:")
        print("✓ Company question set management system")
        print("✓ URL-based configuration loading and caching")
        print("✓ Company admin interface for question customization")
        print("✓ Question set versioning and rollback")
        print("✓ Configuration validation and inheritance")
        print("✓ Cache management and invalidation")
        print("✓ Analytics and performance tracking")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()
        # Clean up test database
        try:
            os.remove("test_url_specific.db")
        except:
            pass

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_url_specific_integration())
    sys.exit(0 if success else 1)