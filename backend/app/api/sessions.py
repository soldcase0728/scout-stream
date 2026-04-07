from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session as DBSession, joinedload

from app.database import get_db
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.models.session import Session
from app.models.swing import Swing
from app.api.auth import get_current_coach
from app.schemas.session import SessionCreate, SessionResponse
from app.schemas.swing import SwingResponse
from app.services.upload import save_upload
from app.services.processing import submit_processing_job

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(
    req: SessionCreate,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    athlete = (
        db.query(Athlete)
        .filter(Athlete.id == req.athlete_id, Athlete.coach_id == coach.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    session = Session(coach_id=coach.id, **req.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.coach_id == coach.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/swings", response_model=list[SwingResponse])
def list_session_swings(
    session_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.coach_id == coach.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    swings = (
        db.query(Swing)
        .filter(Swing.session_id == session_id)
        .options(
            joinedload(Swing.event_review),
            joinedload(Swing.metric_snapshot),
            joinedload(Swing.interpretation),
        )
        .all()
    )
    return [_swing_to_response(s) for s in swings]


@router.post("/{session_id}/swings/upload", response_model=SwingResponse, status_code=201)
async def upload_swing(
    session_id: str,
    file: UploadFile = File(...),
    swing_type: str = Form("regular"),
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    session = (
        db.query(Session)
        .filter(Session.id == session_id, Session.coach_id == coach.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    filepath = await save_upload(file, session_id)
    swing = Swing(
        session_id=session_id,
        swing_type=swing_type,
        source_video_url=filepath,
    )
    db.add(swing)
    db.commit()
    db.refresh(swing)
    submit_processing_job(db, swing)
    return _swing_to_response(swing)


def _swing_to_response(swing: Swing) -> SwingResponse:
    resp = SwingResponse(
        id=swing.id,
        session_id=swing.session_id,
        swing_type=swing.swing_type,
        source_video_url=swing.source_video_url,
        processed_data_url=swing.processed_data_url,
        status=swing.status,
        pipeline_version=swing.pipeline_version,
        notes=swing.notes,
    )
    if swing.event_review:
        er = swing.event_review
        resp.events = {
            "auto_start": er.auto_start_frame,
            "auto_launch": er.auto_launch_frame,
            "auto_contact": er.auto_contact_frame,
            "final_start": er.final_start_frame,
            "final_launch": er.final_launch_frame,
            "final_contact": er.final_contact_frame,
            "manual_override": er.manual_override,
            "confidence": er.event_confidence,
        }
    if swing.metric_snapshot:
        ms = swing.metric_snapshot
        resp.metrics = ms.metrics_json
        resp.deltas = ms.deltas_json
        resp.timing = ms.timing_json
        resp.confidence = {"landmark_confidence": ms.landmark_confidence}
    if swing.interpretation:
        interp = swing.interpretation
        resp.interpretation = {
            "what_happened": interp.what_happened,
            "what_it_means": interp.what_it_means,
            "what_to_coach_next": interp.what_to_coach_next,
            "rules_triggered": interp.rules_triggered,
            "severity": interp.severity,
        }
    return resp
