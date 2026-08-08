"""Celery application configuration for CryptoBroker worker."""
import os
import logging
from celery import Celery
from celery.signals import worker_init, worker_shutdown

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
backend_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "cryptobroker",
    broker=broker_url,
    backend=backend_url,
    include=["app.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_routes={
        "app.tasks.execute_order": {"queue": "orders"},
        "app.tasks.settle_order": {"queue": "orders"},
        "app.tasks.fail_order": {"queue": "orders"},
        "app.tasks.health_check": {"queue": "default"},
    },
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "orders": {
            "exchange": "orders",
            "routing_key": "orders",
        },
    },
)


@worker_init.connect
def init_worker(**kwargs):
    """Initialize worker process."""
    logger.info("CryptoBroker worker initializing...")
    
    # Initialize database session for async tasks
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.tasks import init_db_session
        
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@db:5432/cryptobroker",
        )
        
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        
        init_db_session(engine)
        logger.info("Worker database session initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database session: {e}")
        raise


@worker_shutdown.connect
def shutdown_worker(**kwargs):
    """Cleanup on worker shutdown."""
    logger.info("CryptoBroker worker shutting down...")
    
    # Dispose database engine
    try:
        from app.tasks import _db_session_factory
        
        if _db_session_factory and hasattr(_db_session_factory, "kw"):
            engine = _db_session_factory.kw.get("bind")
            if engine:
                import asyncio
                asyncio.run(engine.dispose())
                logger.info("Database engine disposed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Worker shutdown complete")

