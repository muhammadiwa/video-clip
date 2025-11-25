"""
Celery Worker Startup Script

Run this script to start the Celery worker:
    python celery_worker.py

Or use Celery CLI directly:
    celery -A app.core.celery_app worker --loglevel=info
"""

from app.core.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start()
