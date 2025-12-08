"""APScheduler setup for background task scheduling."""
import logging
import os
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
    
    # Only initialize scheduler in the first worker process to avoid conflicts
    # Check for Heroku dyno name or worker ID
    dyno_name = os.environ.get('DYNO', '')
    worker_id = os.environ.get('WORKER_ID', '0')
    
    # On Heroku, initialize on any web dyno (web.1, web.2, etc.)
    # In other environments, only initialize on worker 0
    if dyno_name:
        if not dyno_name.startswith('web'):
            logger.info(f"⏭️ Skipping scheduler initialization on non-web dyno {dyno_name}")
            return None
        else:
            logger.info(f"✅ Initializing scheduler on dyno {dyno_name}")
    elif worker_id != '0':
        logger.info(f"⏭️ Skipping scheduler initialization in worker {worker_id}")
        return None
    
    try:
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
    except Exception as e:
        logger.error(f"❌ Failed to initialize scheduler: {e}")
        return None


def get_scheduler():
    """Get the scheduler instance."""
    global scheduler
    
    # If scheduler is None, try to initialize it
    if scheduler is None:
        logger.info("🔄 Scheduler not initialized, attempting to initialize now...")
        scheduler = init_scheduler()
    
    if scheduler is None:
        dyno_name = os.environ.get('DYNO', 'unknown')
        error_msg = f"Scheduler not available on this dyno ({dyno_name}). Scheduler only runs on web dynos."
        logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("🛑 APScheduler shut down")
