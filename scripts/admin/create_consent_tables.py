"""
Database migration script to add PDPL-compliant consent tables
Run this script to update the database schema with consent management tables
"""
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base
from app.models import User  # Import User model for foreign key reference
from app.models_consent import UserConsent, ConsentAuditLog, DataProcessingActivity, DataSubjectRequest

def create_consent_tables():
    """Create all consent-related tables"""
    print("Creating PDPL-compliant consent management tables...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine, tables=[
            UserConsent.__table__,
            ConsentAuditLog.__table__,
            DataProcessingActivity.__table__,
            DataSubjectRequest.__table__
        ])
        
        print("✅ Successfully created consent tables:")
        print("   - user_consents")
        print("   - consent_audit_logs")
        print("   - data_processing_activities")
        print("   - data_subject_requests")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_consent_tables()
