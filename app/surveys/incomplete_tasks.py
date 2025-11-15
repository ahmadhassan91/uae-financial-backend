"""
Background tasks for managing incomplete surveys.

This module contains scheduled tasks for:
1. Marking surveys as abandoned after 24 hours of inactivity
2. Cleaning up expired surveys (30+ days old)
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import SessionLocal
from app.models import IncompleteSurvey
import logging

logger = logging.getLogger(__name__)


def mark_abandoned_surveys():
    """
    Mark surveys as abandoned if they haven't been updated in 24 hours.
    
    This should be run periodically (e.g., every hour via cron job or scheduler).
    """
    db = SessionLocal()
    try:
        # Calculate 24 hours ago
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Find surveys that are:
        # 1. Not already marked as abandoned
        # 2. Last activity was more than 24 hours ago
        surveys_to_abandon = db.query(IncompleteSurvey).filter(
            and_(
                IncompleteSurvey.is_abandoned == False,
                IncompleteSurvey.last_activity < twenty_four_hours_ago
            )
        ).all()
        
        count = 0
        for survey in surveys_to_abandon:
            survey.is_abandoned = True
            survey.abandoned_at = datetime.utcnow()
            count += 1
        
        db.commit()
        
        logger.info(f"✅ Marked {count} surveys as abandoned")
        return count
        
    except Exception as e:
        logger.error(f"❌ Error marking abandoned surveys: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_expired_surveys():
    """
    Delete surveys that are older than 30 days.
    
    This should be run periodically (e.g., daily via cron job).
    """
    db = SessionLocal()
    try:
        # Calculate 30 days ago
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Find and delete expired surveys
        expired_surveys = db.query(IncompleteSurvey).filter(
            IncompleteSurvey.started_at < thirty_days_ago
        ).all()
        
        count = len(expired_surveys)
        
        for survey in expired_surveys:
            db.delete(survey)
        
        db.commit()
        
        logger.info(f"✅ Cleaned up {count} expired surveys")
        return count
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up expired surveys: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_task_status() -> dict:
    """Get status information about incomplete surveys."""
    db = SessionLocal()
    try:
        total = db.query(IncompleteSurvey).count()
        abandoned = db.query(IncompleteSurvey).filter(
            IncompleteSurvey.is_abandoned == True
        ).count()
        active = total - abandoned
        
        return {
            "total_surveys": total,
            "active_surveys": active,
            "abandoned_surveys": abandoned,
            "last_check": datetime.utcnow().isoformat()
        }
    finally:
        db.close()


# For manual testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔄 Running abandoned survey marking task...")
    abandoned_count = mark_abandoned_surveys()
    print(f"   Marked {abandoned_count} surveys as abandoned")
    
    print("\n🔄 Getting task status...")
    status = get_task_status()
    print(f"   Total: {status['total_surveys']}")
    print(f"   Active: {status['active_surveys']}")
    print(f"   Abandoned: {status['abandoned_surveys']}")
    
    print("\n✅ Tasks completed")
