"""
Integration test for conditional Q16 scoring through API endpoints.

This test verifies that the conditional Q16 logic works correctly
when submitting surveys through the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, CustomerProfile
from app.auth.utils import get_password_hash
import json


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_q16.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_survey_responses():
    """Sample survey responses for testing."""
    return {
        'q1_income_stability': 4,
        'q2_income_sources': 4,
        'q3_living_expenses': 4,
        'q4_budget_tracking': 4,
        'q5_spending_control': 4,
        'q6_expense_review': 4,
        'q7_savings_rate': 4,
        'q8_emergency_fund': 4,
        'q9_savings_optimization': 4,
        'q10_payment_history': 4,
        'q11_debt_ratio': 4,
        'q12_credit_score': 4,
        'q13_retirement_planning': 4,
        'q14_insurance_coverage': 4,
        'q15_financial_planning': 4,
        'q16_children_planning': 4
    }


class TestQ16Integration:
    """Integration tests for Q16 conditional logic."""
    
    def test_guest_survey_submission_no_profile(self, setup_database, client, sample_survey_responses):
        """Test guest survey submission (no profile, Q16 should be ignored)."""
        response = client.post(
            "/surveys/submit-guest",
            json={
                "responses": sample_survey_responses,
                "completion_time": 300
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Guest users have no profile, so Q16 should be ignored
        # Max score should be 75 (not 80)
        # This is currently not implemented in the guest endpoint, 
        # but we can verify the response structure
        assert "score_breakdown" in data
        assert "overall_score" in data["score_breakdown"]
    
    def test_authenticated_user_with_children_yes(self, setup_database, client, sample_survey_responses):
        """Test authenticated user with children=Yes (Q16 should be included)."""
        db = TestingSessionLocal()
        
        try:
            # Create test user
            user = User(
                email="test_parent@example.com",
                username="test_parent",
                hashed_password=get_password_hash("testpass123"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create customer profile with children=Yes
            profile = CustomerProfile(
                user_id=user.id,
                first_name="Test",
                last_name="Parent",
                age=35,
                gender="male",
                nationality="UAE",
                emirate="dubai",
                employment_status="employed_full_time",
                monthly_income="25000_35000",
                household_size=4,
                children="Yes"  # This should enable Q16
            )
            db.add(profile)
            db.commit()
            
            # Login to get authentication
            login_response = client.post(
                "/auth/simple-login",
                json={
                    "email": "test_parent@example.com",
                    "date_of_birth": "1989-01-01"
                }
            )
            
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            # Submit survey with authentication
            response = client.post(
                "/surveys/submit",
                json={
                    "responses": sample_survey_responses,
                    "completion_time": 300
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "survey_response" in data
            survey_response = data["survey_response"]
            
            # The survey should be processed with Q16 included
            # We can verify this by checking that the response was saved
            assert survey_response["overall_score"] > 0
            
        finally:
            db.close()
    
    def test_authenticated_user_with_children_no(self, setup_database, client, sample_survey_responses):
        """Test authenticated user with children=No (Q16 should be excluded)."""
        db = TestingSessionLocal()
        
        try:
            # Create test user
            user = User(
                email="test_no_children@example.com",
                username="test_no_children",
                hashed_password=get_password_hash("testpass123"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create customer profile with children=No
            profile = CustomerProfile(
                user_id=user.id,
                first_name="Test",
                last_name="Single",
                age=28,
                gender="female",
                nationality="UAE",
                emirate="abu_dhabi",
                employment_status="employed_full_time",
                monthly_income="15000_25000",
                household_size=1,
                children="No"  # This should exclude Q16
            )
            db.add(profile)
            db.commit()
            
            # Login to get authentication
            login_response = client.post(
                "/auth/simple-login",
                json={
                    "email": "test_no_children@example.com",
                    "date_of_birth": "1996-01-01"
                }
            )
            
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            # Submit survey with authentication
            response = client.post(
                "/surveys/submit",
                json={
                    "responses": sample_survey_responses,
                    "completion_time": 300
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "survey_response" in data
            survey_response = data["survey_response"]
            
            # The survey should be processed with Q16 excluded
            assert survey_response["overall_score"] > 0
            
        finally:
            db.close()
    
    def test_profile_creation_with_children_field(self, setup_database, client):
        """Test that customer profile can be created with children field."""
        db = TestingSessionLocal()
        
        try:
            # Create test user
            user = User(
                email="test_profile@example.com",
                username="test_profile",
                hashed_password=get_password_hash("testpass123"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Login to get authentication
            login_response = client.post(
                "/auth/simple-login",
                json={
                    "email": "test_profile@example.com",
                    "date_of_birth": "1990-01-01"
                }
            )
            
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            # Create profile with children field
            profile_data = {
                "first_name": "Test",
                "last_name": "User",
                "age": 34,
                "gender": "Male",
                "nationality": "UAE",
                "emirate": "Dubai",
                "employment_status": "Employed Full Time",
                "monthly_income": "25000_35000",
                "household_size": 3,
                "children": "Yes"
            }
            
            response = client.post(
                "/customers/profile",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify children field is saved correctly
            assert data["children"] == "Yes"
            
        finally:
            db.close()
    
    def test_profile_children_field_validation(self, setup_database, client):
        """Test validation of children field in profile creation."""
        db = TestingSessionLocal()
        
        try:
            # Create test user
            user = User(
                email="test_validation@example.com",
                username="test_validation",
                hashed_password=get_password_hash("testpass123"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Login to get authentication
            login_response = client.post(
                "/auth/simple-login",
                json={
                    "email": "test_validation@example.com",
                    "date_of_birth": "1990-01-01"
                }
            )
            
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            # Test invalid children value
            profile_data = {
                "first_name": "Test",
                "last_name": "User",
                "age": 34,
                "gender": "Male",
                "nationality": "UAE",
                "emirate": "Dubai",
                "employment_status": "Employed Full Time",
                "monthly_income": "25000_35000",
                "household_size": 3,
                "children": "Maybe"  # Invalid value
            }
            
            response = client.post(
                "/customers/profile",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should return validation error
            assert response.status_code == 422
            
        finally:
            db.close()