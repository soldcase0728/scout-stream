"""Service layer for triggering and managing swing processing jobs."""

import logging

from sqlalchemy.orm import Session as DBSession

from app.models.swing import Swing, SwingStatus
from app.models.metric_snapshot import MetricSnapshot
from app.models.interpretation import Interpretation

logger = logging.getLogger(__name__)


def submit_processing_job(db: DBSession, swing: Swing) -> None:
    """Submit a swing for background processing via Celery."""
    swing.status = SwingStatus.QUEUED
    db.commit()

    from processing.tasks import process_swing_task

    process_swing_task.delay(swing.id)


def recompute_after_event_edit(db: DBSession, swing: Swing) -> None:
    """Recompute metrics and interpretation synchronously after manual event frame edit.

    This runs synchronously because the landmark data already exists -
    we only need to recalculate metrics at the new event frames and
    rerun the interpretation rules, which is fast.
    """
    from processing.motion_adapter import extract_landmarks
    from processing.metrics_engine import compute_all_metrics
    from processing.interpretation_engine import interpret_swing

    er = swing.event_review
    if not er:
        return

    # Re-extract landmarks from video (needed to compute metrics at new frames)
    series = extract_landmarks(swing.source_video_url)

    # Determine handedness
    handedness = "right"
    session = swing.session
    if session and session.athlete:
        handedness = session.athlete.handedness

    # Recompute metrics at the new event frames
    result = compute_all_metrics(
        series,
        er.final_start_frame,
        er.final_launch_frame,
        er.final_contact_frame,
        handedness=handedness,
    )

    # Update metric snapshot
    if swing.metric_snapshot:
        swing.metric_snapshot.metrics_json = result["metrics"]
        swing.metric_snapshot.deltas_json = result["deltas"]
        swing.metric_snapshot.timing_json = result["timing"]
        swing.metric_snapshot.landmark_confidence = series.mean_visibility()
    else:
        ms = MetricSnapshot(
            swing_id=swing.id,
            metrics_json=result["metrics"],
            deltas_json=result["deltas"],
            timing_json=result["timing"],
            landmark_confidence=series.mean_visibility(),
        )
        db.add(ms)

    # Reinterpret
    interp_result = interpret_swing(
        result["metrics"], result["deltas"], result["timing"], swing.swing_type
    )

    if swing.interpretation:
        swing.interpretation.what_happened = interp_result["what_happened"]
        swing.interpretation.what_it_means = interp_result["what_it_means"]
        swing.interpretation.what_to_coach_next = interp_result["what_to_coach_next"]
        swing.interpretation.rules_triggered = interp_result["rules_triggered"]
        swing.interpretation.severity = interp_result["severity"]
    else:
        interp = Interpretation(
            swing_id=swing.id,
            what_happened=interp_result["what_happened"],
            what_it_means=interp_result["what_it_means"],
            what_to_coach_next=interp_result["what_to_coach_next"],
            rules_triggered=interp_result["rules_triggered"],
            severity=interp_result["severity"],
        )
        db.add(interp)

    db.commit()
    db.refresh(swing)
    logger.info(f"Recomputed metrics for swing {swing.id} at frames {er.final_start_frame}/{er.final_launch_frame}/{er.final_contact_frame}")
