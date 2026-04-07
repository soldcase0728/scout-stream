"""Service layer for triggering and managing swing processing jobs."""

from sqlalchemy.orm import Session as DBSession

from app.models.swing import Swing, SwingStatus


def submit_processing_job(db: DBSession, swing: Swing) -> None:
    """Submit a swing for background processing via Celery."""
    swing.status = SwingStatus.QUEUED
    db.commit()

    from processing.tasks import process_swing_task

    process_swing_task.delay(swing.id)


def recompute_after_event_edit(db: DBSession, swing: Swing) -> None:
    """Recompute metrics and interpretation after manual event frame edit."""
    from processing.tasks import recompute_swing_task

    recompute_swing_task.delay(swing.id)
