"""Celery worker entry point.

Run with: celery -A processing.worker worker --loglevel=info
"""

from celery import Celery

from app.config import settings

celery_app = Celery("scout-stream", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
)

# Import tasks so they register with the worker
import processing.tasks  # noqa: F401, E402
