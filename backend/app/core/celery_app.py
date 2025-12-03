from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "viral_clip_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.video_tasks", "app.tasks.ai_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json", "pickle"],  # Allow both for compatibility
    result_serializer="json",  # Use JSON for better compatibility
    result_accept_content=["json", "pickle"],  # Accept both when reading results
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # Auto-expire results after 1 hour
    result_extended=True,
    
    # Redis connection pool settings to prevent timeouts during long tasks
    broker_pool_limit=10,  # Limit connection pool size
    broker_heartbeat=30,  # Send heartbeat every 30 seconds to keep connection alive
    broker_connection_retry=True,  # Retry on connection failures
    broker_connection_max_retries=10,  # Max retries before giving up
    
    # Redis transport options for better connection handling
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 hour visibility
        'socket_keepalive': True,  # Enable TCP keepalive
        'socket_timeout': 120,  # Socket timeout 120 seconds
        'socket_connect_timeout': 30,  # Connection timeout 30 seconds
        'retry_on_timeout': True,
        'health_check_interval': 30,  # Check connection health every 30 seconds
    },
    
    # Result backend transport options
    result_backend_transport_options={
        'socket_keepalive': True,
        'socket_timeout': 120,
        'socket_connect_timeout': 30,
        'retry_on_timeout': True,
        'health_check_interval': 30,
    },
)
