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
    
    # On Heroku, only initialize on web.1 dyno
    # In other environments, only initialize on worker 0
    if dyno_name and not dyno_name.startswith('web.1'):
        logger.info(f"⏭️ Skipping scheduler initialization on dyno {dyno_name}")
        return None
    elif not dyno_name and worker_id != '0':
        logger.info(f"⏭️ Skipping scheduler initialization in worker {worker_id}")
        return None
    
    try:
        # Use the database_url property which handles postgres:// to postgresql+psycopg2:// conversion
        database_url = settings.database_url
        logger.info(f"🔧 Using database URL for scheduler (dialect: {database_url.split(':')[0]})")
        
        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=database_url)
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
        logger.error(f"❌ Failed to initialize scheduler: {e}", exc_info=True)
        return None


def get_scheduler():
    """Get the scheduler instance."""
    global scheduler
    
    # If scheduler is None, try to initialize it
    if scheduler is None:
        logger.info("🔄 Scheduler not initialized, attempting to initialize now...")
        try:
            scheduler = init_scheduler()
        except Exception as e:
            logger.error(f"❌ Failed to initialize scheduler: {e}")
            # Don't raise here, let the check below handle it
    
    if scheduler is None:
        dyno_name = os.environ.get('DYNO', 'unknown')
        worker_id = os.environ.get('WORKER_ID', 'unknown')
        error_msg = f"Scheduler not available (DYNO={dyno_name}, WORKER_ID={worker_id}). Scheduler only runs on web dynos or worker 0."
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
