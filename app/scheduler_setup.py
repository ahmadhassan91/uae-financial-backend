"""APScheduler setup for background task scheduling."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from app.config import settings

logger = logging.getLogger(__name__)

# Create scheduler instance (will be initialized in main.py)
scheduler = None


def init_scheduler():
    """Initialize APScheduler with SQLAlchemy job store."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
    
    # Configure job stores
    jobstores = {
        'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
    }
    
    # Configure executors
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    
    # Job defaults
    job_defaults = {
        'coalesce': False,  # Run all missed executions
        'max_instances': 3,  # Allow up to 3 concurrent instances
        'misfire_grace_time': 300  # 5 minutes grace time for missed jobs
    }
    
    # Create scheduler
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("✅ APScheduler initialized and started")
    
    return scheduler


def get_scheduler():
    """Get the scheduler instance."""
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("🛑 APScheduler shut down")
