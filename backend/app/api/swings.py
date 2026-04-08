import json
import os
import base64

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession, joinedload

from app.database import get_db
from app.models.coach import Coach
from app.models.swing import Swing
from app.models.session import Session
from app.models.event_review import EventReview
from app.api.auth import get_current_coach
from app.api.sessions import _swing_to_response
from app.schemas.swing import SwingResponse, EventEditRequest, SwingNotesRequest
from app.services.processing import recompute_after_event_edit

router = APIRouter(prefix="/api/swings", tags=["swings"])


def _get_swing_for_coach(swing_id: str, coach: Coach, db: DBSession) -> Swing:
    swing = (
        db.query(Swing)
        .join(Session)
        .filter(Swing.id == swing_id, Session.coach_id == coach.id)
        .options(
            joinedload(Swing.event_review),
            joinedload(Swing.metric_snapshot),
            joinedload(Swing.interpretation),
        )
        .first()
    )
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")
    return swing


@router.get("/{swing_id}", response_model=SwingResponse)
def get_swing(
    swing_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    swing = _get_swing_for_coach(swing_id, coach, db)
    return _swing_to_response(swing)


@router.get("/{swing_id}/status")
def get_swing_status(
    swing_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    swing = _get_swing_for_coach(swing_id, coach, db)
    return {"id": swing.id, "status": swing.status}


@router.patch("/{swing_id}/events", response_model=SwingResponse)
def edit_events(
    swing_id: str,
    req: EventEditRequest,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    swing = _get_swing_for_coach(swing_id, coach, db)
    if not swing.event_review:
        raise HTTPException(status_code=400, detail="Swing has no event data yet")
    if not (req.final_start_frame < req.final_launch_frame < req.final_contact_frame):
        raise HTTPException(status_code=400, detail="Events must be ordered: start < launch < contact")

    er = swing.event_review
    er.final_start_frame = req.final_start_frame
    er.final_launch_frame = req.final_launch_frame
    er.final_contact_frame = req.final_contact_frame
    er.manual_override = True
    db.commit()

    recompute_after_event_edit(db, swing)

    # Reload with fresh relationships after recompute
    db.expire(swing)
    swing = _get_swing_for_coach(swing_id, coach, db)
    return _swing_to_response(swing)


@router.patch("/{swing_id}/notes", response_model=SwingResponse)
def update_notes(
    swing_id: str,
    req: SwingNotesRequest,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    swing = _get_swing_for_coach(swing_id, coach, db)
    swing.notes = req.notes
    db.commit()
    db.refresh(swing)
    return _swing_to_response(swing)


@router.get("/{swing_id}/comparison/{other_id}")
def compare_swings(
    swing_id: str,
    other_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    swing_a = _get_swing_for_coach(swing_id, coach, db)
    swing_b = _get_swing_for_coach(other_id, coach, db)
    return {
        "swing_a": _swing_to_response(swing_a),
        "swing_b": _swing_to_response(swing_b),
    }


@router.get("/{swing_id}/landmarks")
def get_swing_landmarks(
    swing_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    """Return landmark data at event frames for skeleton overlay."""
    swing = _get_swing_for_coach(swing_id, coach, db)
    if not swing.processed_data_url or not os.path.exists(swing.processed_data_url):
        raise HTTPException(status_code=404, detail="Processed data not available")
    with open(swing.processed_data_url) as f:
        data = json.load(f)
    return data.get("event_landmarks", {})


@router.get("/{swing_id}/drills")
def get_swing_drills(
    swing_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    """Return drill recommendations based on triggered rules for this swing."""
    swing = _get_swing_for_coach(swing_id, coach, db)
    if not swing.interpretation:
        return {"drills": []}
    rule_ids = [r["rule_id"] for r in (swing.interpretation.rules_triggered or [])]
    from processing.drills import get_drills_for_rules
    return {"drills": get_drills_for_rules(rule_ids)}


@router.get("/{swing_id}/frames")
def get_swing_frame_images(
    swing_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    """Extract actual video frame images at event frames as base64 JPEGs.

    Reads frames sequentially (same as motion_adapter) to ensure frame
    indices match what MediaPipe processed. Using cap.set(POS_FRAMES)
    can give wrong frames on variable-framerate phone videos.
    """
    import cv2

    swing = _get_swing_for_coach(swing_id, coach, db)
    if not swing.source_video_url or not os.path.exists(swing.source_video_url):
        raise HTTPException(status_code=404, detail="Video not available")
    if not swing.event_review:
        raise HTTPException(status_code=400, detail="No events detected yet")

    er = swing.event_review
    target_frames = {
        er.final_start_frame: "start",
        er.final_launch_frame: "launch",
        er.final_contact_frame: "contact",
    }
    max_frame = max(target_frames.keys())

    cap = cv2.VideoCapture(swing.source_video_url)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Cannot open video")

    result = {}
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx in target_frames:
            event_name = target_frames[frame_idx]
            h, w = frame.shape[:2]
            scale = min(400 / w, 500 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(frame, (new_w, new_h))
            _, buf = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
            result[event_name] = {
                "image": base64.b64encode(buf).decode('utf-8'),
                "width": new_w,
                "height": new_h,
                "frame_index": frame_idx,
            }
        if frame_idx > max_frame:
            break
        frame_idx += 1

    cap.release()
    return result
