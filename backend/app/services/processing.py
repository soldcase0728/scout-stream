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
    """Recompute metrics and interpretation synchronously after manual event frame edit."""
    from processing.motion_adapter import extract_landmarks
    from processing.metrics_engine import compute_all_metrics
    from processing.interpretation_engine import interpret_swing

    er = swing.event_review
    if not er:
        logger.warning(f"No event review for swing {swing.id}")
        return

    try:
        logger.info(
            f"Recomputing swing {swing.id} at frames "
            f"{er.final_start_frame}/{er.final_launch_frame}/{er.final_contact_frame}"
        )
        series = extract_landmarks(swing.source_video_url)
        logger.info(f"Extracted {series.num_frames} frames from {swing.source_video_url}")

        # Validate frame indices against actual frame count
        if er.final_contact_frame >= series.num_frames:
            logger.warning(f"Contact frame {er.final_contact_frame} >= {series.num_frames}, clamping")
            er.final_contact_frame = series.num_frames - 1
        if er.final_launch_frame >= series.num_frames:
            er.final_launch_frame = series.num_frames - 2
        if er.final_start_frame >= series.num_frames:
            er.final_start_frame = 0

        # Determine handedness
        handedness = "right"
        if swing.session and swing.session.athlete:
            handedness = swing.session.athlete.handedness

        # Recompute metrics at the new event frames
        result = compute_all_metrics(
            series,
            er.final_start_frame,
            er.final_launch_frame,
            er.final_contact_frame,
            handedness=handedness,
        )
        logger.info(f"Metrics computed: timing={result['timing']}")

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
        logger.info(f"Interpretation: severity={interp_result['severity']}, rules={[r['rule_id'] for r in interp_result['rules_triggered']]}")

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
        logger.info(f"Recompute complete for swing {swing.id}")

    except Exception as e:
        logger.exception(f"Recompute failed for swing {swing.id}: {e}")
        raise
