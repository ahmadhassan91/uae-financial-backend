"""
Test script for the Dynamic Question Engine implementation.

This script tests the demographic rule engine, question variation service,
and dynamic question selection functionality.
"""
import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.database import Base
from app.models import CustomerProfile, User, DemographicRule, QuestionVariation
from app.surveys.demographic_rule_engine import DemographicRuleEngine
from app.surveys.question_variation_service import QuestionVariationService
from app.surveys.dynamic_question_engine import (
    DynamicQuestionEngine, QuestionSelectionStrategy
)
from app.surveys.sample_demographic_data import populate_sample_data


def create_test_database():
    """Create test database and tables."""
    engine = create_engine("sqlite:///test_dynamic_questions.db", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


def create_test_profiles(db):
    """Create test customer profiles for different demographics."""
    
    # Check if test user already exists
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    
    profiles = []
    
    # UAE Citizen with Islamic finance preference
    profile1 = CustomerProfile(
        user_id=test_user.id,
        first_name="Ahmed",
        last_name="Al Mansouri",
        age=35,
        gender="Male",
        nationality="UAE",
        emirate="Dubai",
        employment_status="Employed",
        industry="Banking",
        monthly_income="30000-50000",
        household_size=4,
        children="Yes",
        education_level="Bachelor's",
        islamic_finance_preference=True,
        preferred_language="en"
    )
    
    # Expatriate professional
    profile2 = CustomerProfile(
        user_id=test_user.id,
        first_name="John",
        last_name="Smith",
        age=28,
        gender="Male",
        nationality="UK",
        emirate="Abu Dhabi",
        employment_status="Employed",
        industry="Technology",
        monthly_income="20000-30000",
        household_size=1,
        children="No",
        education_level="Master's",
        years_in_uae=3,
        islamic_finance_preference=False,
        preferred_language="en"
    )
    
    # Young UAE professional
    profile3 = CustomerProfile(
        user_id=test_user.id,
        first_name="Fatima",
        last_name="Al Zahra",
        age=25,
        gender="Female",
        nationality="UAE",
        emirate="Sharjah",
        employment_status="Employed",
        industry="Education",
        monthly_income="10000-20000",
        household_size=2,
        children="No",
        education_level="Bachelor's",
        years_in_uae=25,  # Born in UAE
        islamic_finance_preference=True,
        preferred_language="ar"
    )
    
    # High-income expat
    profile4 = CustomerProfile(
        user_id=test_user.id,
        first_name="Michael",
        last_name="Johnson",
        age=45,
        gender="Male",
        nationality="USA",
        emirate="Dubai",
        employment_status="Employed",
        industry="Finance",
        monthly_income="100000+",
        household_size=3,
        children="Yes",
        education_level="MBA",
        years_in_uae=8,
        investment_experience="Advanced",
        islamic_finance_preference=False,
        preferred_language="en"
    )
    
    profiles = [profile1, profile2, profile3, profile4]
    
    for profile in profiles:
        db.add(profile)
    
    db.commit()
    
    for profile in profiles:
        db.refresh(profile)
    
    return profiles


async def test_demographic_rule_engine(db, profiles):
    """Test the demographic rule engine."""
    print("\n=== Testing Demographic Rule Engine ===")
    
    rule_engine = DemographicRuleEngine(db)
    
    for i, profile in enumerate(profiles, 1):
        print(f"\nProfile {i}: {profile.first_name} {profile.last_name}")
        print(f"  Nationality: {profile.nationality}")
        print(f"  Age: {profile.age}")
        print(f"  Emirate: {profile.emirate}")
        print(f"  Income: {profile.monthly_income}")
        print(f"  Islamic Finance: {profile.islamic_finance_preference}")
        
        # Evaluate rules
        rule_results = rule_engine.evaluate_rules_for_profile(profile)
        
        print(f"  Matched Rules:")
        for result in rule_results:
            if result.matched:
                print(f"    - {result.rule_name} (Priority: {result.priority})")
                print(f"      Actions: {result.actions}")
        
        # Test question selection
        selection_result = rule_engine.select_questions_for_profile(profile)
        print(f"  Selected Questions: {len(selection_result.selected_questions)}")
        print(f"  Excluded Questions: {selection_result.excluded_questions}")
        print(f"  Added Questions: {selection_result.added_questions}")


def test_question_variation_service(db, profiles):
    """Test the question variation service."""
    print("\n=== Testing Question Variation Service ===")
    
    variation_service = QuestionVariationService(db)
    
    # Test getting variations
    variations = variation_service.get_question_variations(
        base_question_id="q1_income_stability",
        language="en"
    )
    
    print(f"Found {len(variations)} variations for q1_income_stability")
    for var in variations:
        print(f"  - {var.variation_name}: {var.text[:50]}...")
    
    # Test getting best variation for each profile
    for i, profile in enumerate(profiles, 1):
        print(f"\nProfile {i} - Best variations:")
        
        test_questions = ["q1_income_stability", "q7_savings_rate", "q9_savings_optimization"]
        
        for question_id in test_questions:
            best_var = variation_service.get_best_variation_for_profile(
                question_id, profile, profile.preferred_language
            )
            
            if best_var:
                print(f"  {question_id}: {best_var.variation_name}")
            else:
                print(f"  {question_id}: No specific variation (use base)")


async def test_dynamic_question_engine(db, profiles):
    """Test the dynamic question engine."""
    print("\n=== Testing Dynamic Question Engine ===")
    
    # Note: Redis client is None for this test
    question_engine = DynamicQuestionEngine(db, redis_client=None)
    
    strategies = [
        QuestionSelectionStrategy.DEFAULT,
        QuestionSelectionStrategy.DEMOGRAPHIC,
        QuestionSelectionStrategy.HYBRID
    ]
    
    for strategy in strategies:
        print(f"\n--- Testing {strategy.value} strategy ---")
        
        for i, profile in enumerate(profiles, 1):
            print(f"\nProfile {i}: {profile.first_name}")
            
            question_set = await question_engine.get_questions_for_profile(
                profile=profile,
                language=profile.preferred_language,
                strategy=strategy
            )
            
            print(f"  Questions: {len(question_set.questions)}")
            print(f"  Variations used: {len(question_set.variations_used)}")
            print(f"  Strategy: {question_set.strategy_used}")
            
            # Show first few questions
            for j, question in enumerate(question_set.questions[:3]):
                variation_info = ""
                if question.id in question_set.variations_used:
                    variation_info = f" (Variation: {question_set.variations_used[question.id]})"
                print(f"    Q{j+1}: {question.text[:60]}...{variation_info}")
            
            if len(question_set.questions) > 3:
                print(f"    ... and {len(question_set.questions) - 3} more questions")


def test_rule_validation(db):
    """Test rule validation functionality."""
    print("\n=== Testing Rule Validation ===")
    
    rule_engine = DemographicRuleEngine(db)
    
    # Test valid rule
    valid_rule = {
        'conditions': {
            'and': [
                {'nationality': {'eq': 'UAE'}},
                {'age': {'gte': 25}}
            ]
        },
        'actions': {
            'include_questions': ['q1_income_stability', 'q2_income_sources']
        }
    }
    
    validation = rule_engine.validate_rule(valid_rule)
    print(f"Valid rule validation: {validation}")
    
    # Test invalid rule
    invalid_rule = {
        'conditions': {
            'invalid_field': {'eq': 'value'}
        },
        'actions': {
            'invalid_action': ['q1_income_stability']
        }
    }
    
    validation = rule_engine.validate_rule(invalid_rule)
    print(f"Invalid rule validation: {validation}")
    
    # Test potentially discriminatory rule
    discriminatory_rule = {
        'conditions': {
            'gender': {'eq': 'Male'}
        },
        'actions': {
            'include_questions': ['q1_income_stability']
        }
    }
    
    validation = rule_engine.validate_rule(discriminatory_rule)
    print(f"Discriminatory rule validation: {validation}")


def test_question_variation_validation(db):
    """Test question variation validation."""
    print("\n=== Testing Question Variation Validation ===")
    
    variation_service = QuestionVariationService(db)
    
    from app.surveys.question_definitions import question_lookup
    
    base_question = question_lookup.get_question_by_id("q1_income_stability")
    
    # Test valid variation
    valid_options = [
        {'value': 5, 'label': 'Strongly Agree'},
        {'value': 4, 'label': 'Agree'},
        {'value': 3, 'label': 'Neutral'},
        {'value': 2, 'label': 'Disagree'},
        {'value': 1, 'label': 'Strongly Disagree'}
    ]
    
    validation = variation_service.validate_question_variation(
        base_question,
        "My income is very stable and predictable each month.",
        valid_options
    )
    print(f"Valid variation: {validation}")
    
    # Test invalid variation (wrong number of options)
    invalid_options = [
        {'value': 5, 'label': 'Yes'},
        {'value': 1, 'label': 'No'}
    ]
    
    validation = variation_service.validate_question_variation(
        base_question,
        "Do you have stable income?",
        invalid_options
    )
    print(f"Invalid variation: {validation}")


async def run_all_tests():
    """Run all tests."""
    print("Creating test database...")
    engine = create_test_database()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Populating sample data...")
        result = populate_sample_data(db)
        print(f"Sample data result: {result}")
        
        print("Creating test profiles...")
        profiles = create_test_profiles(db)
        
        # Run tests
        await test_demographic_rule_engine(db, profiles)
        test_question_variation_service(db, profiles)
        await test_dynamic_question_engine(db, profiles)
        test_rule_validation(db)
        test_question_variation_validation(db)
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_all_tests())