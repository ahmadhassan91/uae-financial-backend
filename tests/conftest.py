"""
Pytest configuration and shared fixtures for incomplete surveys tests.

This file provides common fixtures used across all test suites.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import settings


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    Uses in-memory SQLite for speed.
    """
    # Create in-memory SQLite database
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with database override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def auth_headers(test_user):
    """
    Create authentication headers for a regular user.
    """
    # In a real implementation, generate JWT token
    # For testing, we can mock this
    from app.auth.utils import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_user.id)})
    
    return {
        "Authorization": f"Bearer {access_token}"
    }


@pytest.fixture
def admin_auth_headers(db):
    """
    Create authentication headers for an admin user.
    """
    from app.models import User
    from app.auth.utils import create_access_token
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password="hashed_password",
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return {
        "Authorization": f"Bearer {access_token}"
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def mock_email_service(monkeypatch):
    """
    Mock email service to avoid sending real emails during tests.
    """
    class MockEmailService:
        sent_emails = []
        
        async def send_reminder_email(self, recipient_email, customer_name, language, resume_link):
            self.sent_emails.append({
                "to": recipient_email,
                "name": customer_name,
                "language": language,
                "link": resume_link
            })
            return True
    
    mock_service = MockEmailService()
    
    # Patch the email service
    monkeypatch.setattr(
        "app.reports.email_service.EmailReportService",
        lambda: mock_service
    )
    
    return mock_service


@pytest.fixture
def mock_sms_service(monkeypatch):
    """
    Mock SMS service to avoid sending real SMS during tests.
    """
    class MockSMSService:
        sent_messages = []
        
        def send_sms(self, phone_number, message):
            self.sent_messages.append({
                "to": phone_number,
                "message": message
            })
            return True
    
    return MockSMSService()


# ============================================================================
# CONFIGURATION
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Set up test environment variables.
    Auto-used for all tests.
    """
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests"
    )


# ============================================================================
# HELPERS
# ============================================================================

@pytest.fixture
def assert_audit_log():
    """
    Helper function to assert audit log entries.
    """
    def _assert_audit_log(db, action, expected_details_substring=None):
        from app.models import AuditLog
        
        audit = db.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(AuditLog.created_at.desc()).first()
        
        assert audit is not None, f"No audit log found for action: {action}"
        
        if expected_details_substring:
            assert expected_details_substring in audit.details, \
                f"Expected '{expected_details_substring}' in audit details"
        
        return audit
    
    return _assert_audit_log
