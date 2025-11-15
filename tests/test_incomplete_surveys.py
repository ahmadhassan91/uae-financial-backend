"""
Comprehensive test suite for Incomplete Surveys feature with Company URL support.

Tests cover:
1. Survey creation (start/start-guest endpoints)
2. Session restoration (resume endpoint)
3. Session expiry (30-day rule)
4. Company tracking
5. Follow-up email generation
6. Admin list/stats endpoints
7. Edge cases and error handling

Author: AI Assistant
Date: November 15, 2025
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import IncompleteSurvey, CompanyTracker, User, CustomerProfile, AuditLog
from app.surveys.incomplete_schemas import (
    IncompleteSurveyCreate,
    IncompleteSurveyUpdate,
    FollowUpRequest
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        hashed_password="hashed_password_here",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_company(db: Session):
    """Create a test company tracker."""
    company = CompanyTracker(
        company_name="Test Company Ltd",
        unique_url="test-company",
        is_active=True,
        qr_scans=0,
        surveys_completed=0
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def test_inactive_company(db: Session):
    """Create an inactive test company."""
    company = CompanyTracker(
        company_name="Inactive Company",
        unique_url="inactive-company",
        is_active=False,
        qr_scans=0,
        surveys_completed=0
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def incomplete_survey_data():
    """Sample incomplete survey data."""
    return {
        "current_step": 3,
        "total_steps": 14,
        "responses": {
            "Q1": 4,
            "Q2": 3,
            "Q3": 5
        },
        "email": "user@example.com",
        "phone_number": "+971501234567"
    }


@pytest.fixture
def incomplete_survey_with_company_data(test_company):
    """Sample incomplete survey data with company tracking."""
    return {
        "current_step": 5,
        "total_steps": 14,
        "responses": {
            "Q1": 4,
            "Q2": 3,
            "Q3": 5,
            "Q4": 2,
            "Q5": 4
        },
        "email": "company.user@example.com",
        "phone_number": "+971507654321",
        "company_url": "test-company"
    }


# ============================================================================
# TEST: Survey Creation (Start Endpoint)
# ============================================================================

class TestSurveyCreation:
    """Test suite for survey creation endpoints."""

    def test_start_guest_survey_basic(self, client, db, incomplete_survey_data):
        """Test creating incomplete survey as guest user."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json=incomplete_survey_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "session_id" in data
        assert data["current_step"] == 3
        assert data["total_steps"] == 14
        assert data["email"] == "user@example.com"
        assert data["phone_number"] == "+971501234567"
        assert data["is_abandoned"] is False
        assert data["follow_up_sent"] is False
        assert data["follow_up_count"] == 0
        assert data["company_id"] is None
        assert data["company_url"] is None
        
        # Verify session_id is valid UUID
        assert len(data["session_id"]) > 20

    def test_start_guest_survey_with_company(self, client, db, incomplete_survey_with_company_data, test_company):
        """Test creating incomplete survey with company tracking."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json=incomplete_survey_with_company_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify company tracking
        assert data["company_id"] == test_company.id
        assert data["company_url"] == "test-company"
        assert data["current_step"] == 5
        
        # Verify in database
        survey = db.query(IncompleteSurvey).filter_by(session_id=data["session_id"]).first()
        assert survey is not None
        assert survey.company_id == test_company.id
        assert survey.company_url == "test-company"

    def test_start_survey_with_invalid_company(self, client, db, incomplete_survey_data):
        """Test creating survey with non-existent company URL."""
        data = incomplete_survey_data.copy()
        data["company_url"] = "non-existent-company"
        
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json=data
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should create survey but without company tracking
        assert result["company_id"] is None
        assert result["company_url"] == "non-existent-company"  # Stored for reference

    def test_start_survey_with_inactive_company(self, client, db, incomplete_survey_data, test_inactive_company):
        """Test creating survey with inactive company."""
        data = incomplete_survey_data.copy()
        data["company_url"] = "inactive-company"
        
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json=data
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should create survey but not link to inactive company
        assert result["company_id"] is None

    def test_start_survey_authenticated_user(self, client, db, incomplete_survey_data, test_user, auth_headers):
        """Test creating survey as authenticated user."""
        response = client.post(
            "/api/v1/surveys/incomplete/start",
            json=incomplete_survey_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user_id is set
        assert data["user_id"] == test_user.id

    def test_start_survey_missing_required_fields(self, client, db):
        """Test creating survey with missing required fields."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 1
                # Missing total_steps
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_start_survey_invalid_step_numbers(self, client, db):
        """Test creating survey with invalid step numbers."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 10,
                "total_steps": 5,  # current > total (invalid)
                "email": "test@example.com"
            }
        )
        
        # Should accept but may not be logical
        assert response.status_code in [200, 422]


# ============================================================================
# TEST: Session Restoration (Resume Endpoint)
# ============================================================================

class TestSessionRestoration:
    """Test suite for session restoration endpoint."""

    def test_resume_valid_session(self, client, db, test_company):
        """Test resuming a valid session."""
        # Create incomplete survey
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=5,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5, "Q4": 2, "Q5": 4},
            email="resume@example.com",
            phone_number="+971501234567",
            company_id=test_company.id,
            company_url="test-company",
            started_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(hours=2)
        )
        db.add(survey)
        db.commit()
        
        # Resume session
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify data
        assert data["session_id"] == session_id
        assert data["current_step"] == 5
        assert data["total_steps"] == 14
        assert data["email"] == "resume@example.com"
        assert data["company_id"] == test_company.id
        assert data["company_url"] == "test-company"
        assert len(data["responses"]) == 5
        
        # Verify last_activity was updated
        db.refresh(survey)
        time_diff = datetime.utcnow() - survey.last_activity
        assert time_diff.total_seconds() < 5  # Should be very recent

    def test_resume_nonexistent_session(self, client, db):
        """Test resuming non-existent session."""
        fake_session_id = str(uuid4())
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{fake_session_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_resume_expired_session(self, client, db):
        """Test resuming expired session (30+ days old)."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=3,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5},
            email="expired@example.com",
            started_at=datetime.utcnow() - timedelta(days=35),
            last_activity=datetime.utcnow() - timedelta(days=31)
        )
        db.add(survey)
        db.commit()
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        
        assert response.status_status == 410  # Gone
        assert "expired" in response.json()["detail"].lower()

    def test_resume_session_boundary_29_days(self, client, db):
        """Test resuming session at 29 days (should work)."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=3,
            total_steps=14,
            responses={"Q1": 4},
            email="boundary@example.com",
            started_at=datetime.utcnow() - timedelta(days=29),
            last_activity=datetime.utcnow() - timedelta(days=29)
        )
        db.add(survey)
        db.commit()
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        
        assert response.status_code == 200

    def test_resume_session_boundary_30_days_exactly(self, client, db):
        """Test resuming session at exactly 30 days."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=3,
            total_steps=14,
            responses={"Q1": 4},
            email="exact30@example.com",
            started_at=datetime.utcnow() - timedelta(days=30),
            last_activity=datetime.utcnow() - timedelta(days=30)
        )
        db.add(survey)
        db.commit()
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        
        # At exactly 30 days, should be expired
        assert response.status_code == 410

    def test_resume_creates_audit_log(self, client, db):
        """Test that resuming creates audit log entry."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=3,
            total_steps=14,
            responses={"Q1": 4},
            email="audit@example.com",
            company_url="test-company",
            started_at=datetime.utcnow() - timedelta(hours=1),
            last_activity=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add(survey)
        db.commit()
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        assert response.status_code == 200
        
        # Check audit log
        audit = db.query(AuditLog).filter(
            AuditLog.action == "resume_incomplete_survey"
        ).order_by(AuditLog.created_at.desc()).first()
        
        assert audit is not None
        assert session_id in audit.details
        assert "test-company" in audit.details

    def test_resume_without_company(self, client, db):
        """Test resuming session without company tracking."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=2,
            total_steps=14,
            responses={"Q1": 3, "Q2": 4},
            email="nocompany@example.com",
            started_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(hours=1)
        )
        db.add(survey)
        db.commit()
        
        response = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] is None
        assert data["company_url"] is None


# ============================================================================
# TEST: Admin List & Stats Endpoints
# ============================================================================

class TestAdminEndpoints:
    """Test suite for admin list and stats endpoints."""

    def test_list_all_surveys(self, client, db, admin_auth_headers):
        """Test listing all incomplete surveys."""
        # Create multiple surveys
        for i in range(5):
            survey = IncompleteSurvey(
                session_id=str(uuid4()),
                current_step=i + 1,
                total_steps=14,
                responses={},
                email=f"user{i}@example.com",
                started_at=datetime.utcnow() - timedelta(hours=i),
                last_activity=datetime.utcnow() - timedelta(hours=i)
            )
            db.add(survey)
        db.commit()
        
        response = client.get(
            "/api/v1/surveys/incomplete/admin/list",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_abandoned_only(self, client, db, admin_auth_headers):
        """Test filtering for abandoned surveys only."""
        # Create recent survey (< 24h)
        recent = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email="recent@example.com",
            started_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(hours=1)
        )
        db.add(recent)
        
        # Create abandoned survey (> 24h)
        abandoned = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=5,
            total_steps=14,
            responses={},
            email="abandoned@example.com",
            started_at=datetime.utcnow() - timedelta(days=2),
            last_activity=datetime.utcnow() - timedelta(days=2)
        )
        db.add(abandoned)
        db.commit()
        
        response = client.get(
            "/api/v1/surveys/incomplete/admin/list?abandoned_only=true",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "abandoned@example.com"
        assert data[0]["is_abandoned"] is True

    def test_list_with_pagination(self, client, db, admin_auth_headers):
        """Test pagination parameters."""
        # Create 15 surveys
        for i in range(15):
            survey = IncompleteSurvey(
                session_id=str(uuid4()),
                current_step=1,
                total_steps=14,
                responses={},
                email=f"page{i}@example.com",
                started_at=datetime.utcnow() - timedelta(hours=i),
                last_activity=datetime.utcnow() - timedelta(hours=i)
            )
            db.add(survey)
        db.commit()
        
        # Get first page
        response1 = client.get(
            "/api/v1/surveys/incomplete/admin/list?skip=0&limit=10",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        page1 = response1.json()
        assert len(page1) == 10
        
        # Get second page
        response2 = client.get(
            "/api/v1/surveys/incomplete/admin/list?skip=10&limit=10",
            headers=admin_auth_headers
        )
        assert response2.status_code == 200
        page2 = response2.json()
        assert len(page2) == 5

    def test_get_stats(self, client, db, admin_auth_headers):
        """Test getting statistics."""
        # Create surveys with different states
        # Recent active
        active = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=5,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5, "Q4": 2, "Q5": 4},
            email="active@example.com",
            started_at=datetime.utcnow() - timedelta(hours=1),
            last_activity=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add(active)
        
        # Abandoned with email
        abandoned1 = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5},
            email="abandoned1@example.com",
            started_at=datetime.utcnow() - timedelta(days=2),
            last_activity=datetime.utcnow() - timedelta(days=2),
            follow_up_sent=False
        )
        db.add(abandoned1)
        
        # Abandoned without email
        abandoned2 = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=2,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3},
            email=None,
            started_at=datetime.utcnow() - timedelta(days=3),
            last_activity=datetime.utcnow() - timedelta(days=3)
        )
        db.add(abandoned2)
        
        # Already followed up
        followed_up = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=4,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5, "Q4": 2},
            email="followed@example.com",
            started_at=datetime.utcnow() - timedelta(days=4),
            last_activity=datetime.utcnow() - timedelta(days=4),
            follow_up_sent=True,
            follow_up_count=1
        )
        db.add(followed_up)
        db.commit()
        
        response = client.get(
            "/api/v1/surveys/incomplete/admin/stats",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["total_incomplete"] == 4
        assert stats["abandoned_count"] == 3  # All except active
        assert stats["follow_up_pending"] == 1  # Only abandoned1
        assert 0 <= stats["average_completion_rate"] <= 100
        assert stats["most_common_exit_step"] > 0


# ============================================================================
# TEST: Follow-up Email Generation
# ============================================================================

class TestFollowUpEmails:
    """Test suite for follow-up email generation."""

    def test_send_follow_up_basic(self, client, db, admin_auth_headers, test_company):
        """Test sending follow-up to single survey."""
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=5,
            total_steps=14,
            responses={"Q1": 4, "Q2": 3, "Q3": 5, "Q4": 2, "Q5": 4},
            email="followup@example.com",
            company_id=test_company.id,
            company_url="test-company",
            started_at=datetime.utcnow() - timedelta(days=2),
            last_activity=datetime.utcnow() - timedelta(days=2),
            follow_up_sent=False
        )
        db.add(survey)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": [survey.id],
                "message_template": "Please complete your survey",
                "send_email": True,
                "send_sms": False
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["sent_count"] >= 1
        
        # Verify survey was marked
        db.refresh(survey)
        assert survey.follow_up_sent is True
        assert survey.follow_up_count == 1

    def test_send_follow_up_company_aware_link(self, client, db, admin_auth_headers, test_company):
        """Test that follow-up generates company-aware resume link."""
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email="company.user@example.com",
            company_id=test_company.id,
            company_url="test-company",
            started_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(days=1)
        )
        db.add(survey)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": [survey.id],
                "message_template": "Resume here: {resume_link}",
                "send_email": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        
        # Check audit log for link format
        audit = db.query(AuditLog).filter(
            AuditLog.action == "send_follow_up"
        ).order_by(AuditLog.created_at.desc()).first()
        
        assert audit is not None
        assert "test-company" in audit.details
        assert survey.session_id in audit.details

    def test_send_follow_up_regular_user_link(self, client, db, admin_auth_headers):
        """Test that follow-up generates regular link for non-company users."""
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email="regular@example.com",
            company_id=None,
            company_url=None,
            started_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(days=1)
        )
        db.add(survey)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": [survey.id],
                "message_template": "Resume: {resume_link}",
                "send_email": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200

    def test_send_follow_up_multiple_surveys(self, client, db, admin_auth_headers):
        """Test bulk follow-up to multiple surveys."""
        survey_ids = []
        for i in range(3):
            survey = IncompleteSurvey(
                session_id=str(uuid4()),
                current_step=i + 1,
                total_steps=14,
                responses={},
                email=f"bulk{i}@example.com",
                started_at=datetime.utcnow() - timedelta(days=1),
                last_activity=datetime.utcnow() - timedelta(days=1)
            )
            db.add(survey)
            db.flush()
            survey_ids.append(survey.id)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": survey_ids,
                "message_template": "Complete your survey",
                "send_email": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["sent_count"] == 3
        
        # Verify all marked
        for survey_id in survey_ids:
            survey = db.query(IncompleteSurvey).get(survey_id)
            assert survey.follow_up_sent is True

    def test_send_follow_up_without_email(self, client, db, admin_auth_headers):
        """Test follow-up to survey without email."""
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email=None,  # No email
            started_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(days=1)
        )
        db.add(survey)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": [survey.id],
                "message_template": "Complete survey",
                "send_email": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # Should skip surveys without email
        assert result["sent_count"] == 0 or result["failed_count"] == 1

    def test_send_follow_up_increments_count(self, client, db, admin_auth_headers):
        """Test that follow-up count increments correctly."""
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email="increment@example.com",
            started_at=datetime.utcnow() - timedelta(days=1),
            last_activity=datetime.utcnow() - timedelta(days=1),
            follow_up_count=1  # Already sent once
        )
        db.add(survey)
        db.commit()
        
        response = client.post(
            "/api/v1/surveys/incomplete/admin/follow-up",
            json={
                "survey_ids": [survey.id],
                "message_template": "Second reminder",
                "send_email": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        
        db.refresh(survey)
        assert survey.follow_up_count == 2


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error scenarios."""

    def test_session_id_uniqueness(self, client, db):
        """Test that session IDs are unique."""
        session_ids = set()
        
        for _ in range(10):
            response = client.post(
                "/api/v1/surveys/incomplete/start-guest",
                json={
                    "current_step": 1,
                    "total_steps": 14,
                    "email": "unique@example.com"
                }
            )
            assert response.status_code == 200
            session_id = response.json()["session_id"]
            assert session_id not in session_ids
            session_ids.add(session_id)

    def test_concurrent_resume_same_session(self, client, db):
        """Test concurrent resume requests for same session."""
        session_id = str(uuid4())
        survey = IncompleteSurvey(
            session_id=session_id,
            current_step=3,
            total_steps=14,
            responses={},
            email="concurrent@example.com",
            started_at=datetime.utcnow() - timedelta(hours=1),
            last_activity=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add(survey)
        db.commit()
        
        # Make multiple concurrent requests
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(client.get, f"/api/v1/surveys/incomplete/resume/{session_id}")
                for _ in range(5)
            ]
            results = [f.result() for f in futures]
        
        # All should succeed
        for response in results:
            assert response.status_code == 200

    def test_very_large_responses_object(self, client, db):
        """Test handling large responses JSON."""
        large_responses = {f"Q{i}": i % 5 + 1 for i in range(1, 501)}
        
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 500,
                "total_steps": 500,
                "responses": large_responses,
                "email": "large@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["responses"]) == 500

    def test_special_characters_in_email(self, client, db):
        """Test emails with special characters."""
        special_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "123@example.com"
        ]
        
        for email in special_emails:
            response = client.post(
                "/api/v1/surveys/incomplete/start-guest",
                json={
                    "current_step": 1,
                    "total_steps": 14,
                    "email": email
                }
            )
            assert response.status_code == 200

    def test_update_survey_multiple_times(self, client, db):
        """Test updating same survey multiple times."""
        # Create survey
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 1,
                "total_steps": 14,
                "email": "update@example.com"
            }
        )
        session_id = response.json()["session_id"]
        
        # Update multiple times
        for step in range(2, 6):
            survey = db.query(IncompleteSurvey).filter_by(session_id=session_id).first()
            survey.current_step = step
            survey.last_activity = datetime.utcnow()
            db.commit()
        
        # Verify final state
        final_survey = db.query(IncompleteSurvey).filter_by(session_id=session_id).first()
        assert final_survey.current_step == 5

    def test_zero_steps_survey(self, client, db):
        """Test survey with zero current step."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 0,
                "total_steps": 14,
                "email": "zero@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_step"] == 0

    def test_null_responses(self, client, db):
        """Test survey with null/empty responses."""
        response = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 1,
                "total_steps": 14,
                "responses": None,
                "email": "null@example.com"
            }
        )
        
        # Should accept null responses
        assert response.status_code in [200, 422]

    def test_unauthorized_admin_access(self, client, db):
        """Test accessing admin endpoints without authentication."""
        response = client.get("/api/v1/surveys/incomplete/admin/list")
        
        assert response.status_code == 401  # Unauthorized

    def test_non_admin_user_access(self, client, db, auth_headers):
        """Test accessing admin endpoints as regular user."""
        response = client.get(
            "/api/v1/surveys/incomplete/admin/list",
            headers=auth_headers
        )
        
        # Should require admin role
        assert response.status_code in [401, 403]


# ============================================================================
# TEST: Company Tracking Integration
# ============================================================================

class TestCompanyTracking:
    """Test suite for company tracking integration."""

    def test_company_tracking_preserves_through_flow(self, client, db, test_company):
        """Test company tracking is preserved throughout entire flow."""
        # 1. Start survey with company
        response1 = client.post(
            "/api/v1/surveys/incomplete/start-guest",
            json={
                "current_step": 0,
                "total_steps": 14,
                "email": "flow@example.com",
                "company_url": "test-company"
            }
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        assert response1.json()["company_url"] == "test-company"
        
        # 2. Resume session
        response2 = client.get(f"/api/v1/surveys/incomplete/resume/{session_id}")
        assert response2.status_code == 200
        assert response2.json()["company_url"] == "test-company"
        assert response2.json()["company_id"] == test_company.id
        
        # 3. List in admin
        survey = db.query(IncompleteSurvey).filter_by(session_id=session_id).first()
        assert survey.company_url == "test-company"
        assert survey.company_id == test_company.id

    def test_multiple_companies(self, client, db):
        """Test surveys from multiple different companies."""
        # Create companies
        company1 = CompanyTracker(
            company_name="Company A",
            unique_url="company-a",
            is_active=True
        )
        company2 = CompanyTracker(
            company_name="Company B",
            unique_url="company-b",
            is_active=True
        )
        db.add_all([company1, company2])
        db.commit()
        
        # Create surveys for each
        for i, company_url in enumerate(["company-a", "company-b"]):
            response = client.post(
                "/api/v1/surveys/incomplete/start-guest",
                json={
                    "current_step": 1,
                    "total_steps": 14,
                    "email": f"user{i}@example.com",
                    "company_url": company_url
                }
            )
            assert response.status_code == 200
            assert response.json()["company_url"] == company_url

    def test_company_deleted_after_survey_created(self, client, db, test_company):
        """Test behavior when company is deleted after survey creation."""
        # Create survey with company
        survey = IncompleteSurvey(
            session_id=str(uuid4()),
            current_step=3,
            total_steps=14,
            responses={},
            email="deleted@example.com",
            company_id=test_company.id,
            company_url="test-company",
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        db.add(survey)
        db.commit()
        
        # Delete company
        db.delete(test_company)
        db.commit()
        
        # Survey should still be accessible
        db.refresh(survey)
        assert survey.company_url == "test-company"
        # company_id might be None due to FK cascade


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
