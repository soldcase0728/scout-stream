"""Celery task definitions for swing processing pipeline.

Pipeline: video → landmarks → events → metrics → interpretation
"""

from __future__ import annotations

import json
import logging
import os

from processing.worker import celery_app
from app.config import settings
from app.database import SessionLocal
from app.models.swing import Swing, SwingStatus
from app.models.event_review import EventReview
from app.models.metric_snapshot import MetricSnapshot
from app.models.interpretation import Interpretation

logger = logging.getLogger(__name__)


@celery_app.task(name="process_swing")
def process_swing_task(swing_id: str) -> dict:
    """Full processing pipeline for a new swing upload."""
    db = SessionLocal()
    try:
        swing = db.query(Swing).filter(Swing.id == swing_id).first()
        if not swing:
            return {"error": "Swing not found"}

        swing.status = SwingStatus.PROCESSING
        db.commit()

        # Step 1: Extract landmarks
        from processing.motion_adapter import extract_landmarks

        series = extract_landmarks(swing.source_video_url)
        logger.info(f"Extracted {series.num_frames} frames from {swing.source_video_url}")

        # Save processed data
        os.makedirs(settings.processed_dir, exist_ok=True)
        processed_path = os.path.join(settings.processed_dir, f"{swing_id}.json")
        _save_landmark_data(series, processed_path)
        swing.processed_data_url = processed_path

        # Step 2: Detect events
        from processing.event_detection import detect_events

        events = detect_events(series, swing.swing_type)
        logger.info(
            f"Events: start={events.start_frame}, launch={events.launch_frame}, "
            f"contact={events.contact_frame}, confidence={events.confidence:.2f}"
        )

        # Store event review
        event_review = EventReview(
            swing_id=swing_id,
            auto_start_frame=events.start_frame,
            auto_launch_frame=events.launch_frame,
            auto_contact_frame=events.contact_frame,
            final_start_frame=events.start_frame,
            final_launch_frame=events.launch_frame,
            final_contact_frame=events.contact_frame,
            event_confidence=events.confidence,
        )
        db.add(event_review)

        # Step 3: Compute metrics
        from processing.metrics_engine import compute_all_metrics

        # Determine handedness from athlete
        session = swing.session
        handedness = "right"
        if session and session.athlete:
            handedness = session.athlete.handedness

        result = compute_all_metrics(
            series,
            events.start_frame,
            events.launch_frame,
            events.contact_frame,
            handedness=handedness,
        )

        metric_snapshot = MetricSnapshot(
            swing_id=swing_id,
            metrics_json=result["metrics"],
            deltas_json=result["deltas"],
            timing_json=result["timing"],
            landmark_confidence=series.mean_visibility(),
        )
        db.add(metric_snapshot)

        # Step 4: Interpret
        from processing.interpretation_engine import interpret_swing

        interp_result = interpret_swing(
            result["metrics"], result["deltas"], result["timing"], swing.swing_type
        )

        interpretation = Interpretation(
            swing_id=swing_id,
            what_happened=interp_result["what_happened"],
            what_it_means=interp_result["what_it_means"],
            what_to_coach_next=interp_result["what_to_coach_next"],
            rules_triggered=interp_result["rules_triggered"],
            severity=interp_result["severity"],
        )
        db.add(interpretation)

        swing.status = SwingStatus.REVIEW_READY
        db.commit()

        return {"status": "success", "swing_id": swing_id}

    except Exception as e:
        logger.exception(f"Processing failed for swing {swing_id}")
        swing = db.query(Swing).filter(Swing.id == swing_id).first()
        if swing:
            swing.status = SwingStatus.FAILED
            db.commit()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="recompute_swing")
def recompute_swing_task(swing_id: str) -> dict:
    """Recompute metrics and interpretation after manual event edit."""
    db = SessionLocal()
    try:
        swing = db.query(Swing).filter(Swing.id == swing_id).first()
        if not swing or not swing.processed_data_url:
            return {"error": "Swing or processed data not found"}

        event_review = swing.event_review
        if not event_review:
            return {"error": "No event review found"}

        # Reload landmarks from processed data
        from processing.motion_adapter import extract_landmarks

        series = extract_landmarks(swing.source_video_url)

        # Recompute with final (manually edited) frames
        from processing.metrics_engine import compute_all_metrics

        session = swing.session
        handedness = "right"
        if session and session.athlete:
            handedness = session.athlete.handedness

        result = compute_all_metrics(
            series,
            event_review.final_start_frame,
            event_review.final_launch_frame,
            event_review.final_contact_frame,
            handedness=handedness,
        )

        # Update metric snapshot
        if swing.metric_snapshot:
            swing.metric_snapshot.metrics_json = result["metrics"]
            swing.metric_snapshot.deltas_json = result["deltas"]
            swing.metric_snapshot.timing_json = result["timing"]
        else:
            ms = MetricSnapshot(
                swing_id=swing_id,
                metrics_json=result["metrics"],
                deltas_json=result["deltas"],
                timing_json=result["timing"],
                landmark_confidence=series.mean_visibility(),
            )
            db.add(ms)

        # Reinterpret
        from processing.interpretation_engine import interpret_swing

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
                swing_id=swing_id,
                what_happened=interp_result["what_happened"],
                what_it_means=interp_result["what_it_means"],
                what_to_coach_next=interp_result["what_to_coach_next"],
                rules_triggered=interp_result["rules_triggered"],
                severity=interp_result["severity"],
            )
            db.add(interp)

        db.commit()
        return {"status": "success", "swing_id": swing_id}

    except Exception as e:
        logger.exception(f"Recompute failed for swing {swing_id}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


def _save_landmark_data(series, path: str) -> None:
    """Save landmark time series as JSON for later reprocessing."""
    data = {
        "frame_rate": series.frame_rate,
        "num_frames": series.num_frames,
        "source": series.source,
        "pipeline_version": series.pipeline_version,
    }
    with open(path, "w") as f:
        json.dump(data, f)
