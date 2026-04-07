from fastapi import APIRouter, Depends, HTTPException
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
    db.refresh(swing)
    recompute_after_event_edit(db, swing)
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
