from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.models.session import Session
from app.models.swing import Swing, SwingStatus
from app.models.metric_snapshot import MetricSnapshot
from app.models.interpretation import Interpretation
from app.api.auth import get_current_coach
from app.schemas.athlete import AthleteCreate, AthleteUpdate, AthleteResponse
from app.schemas.session import SessionResponse

router = APIRouter(prefix="/api/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteResponse])
def list_athletes(coach: Coach = Depends(get_current_coach), db: DBSession = Depends(get_db)):
    return db.query(Athlete).filter(Athlete.coach_id == coach.id).all()


@router.post("", response_model=AthleteResponse, status_code=201)
def create_athlete(
    req: AthleteCreate,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    athlete = Athlete(coach_id=coach.id, **req.model_dump())
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("/{athlete_id}", response_model=AthleteResponse)
def get_athlete(
    athlete_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    athlete = (
        db.query(Athlete)
        .filter(Athlete.id == athlete_id, Athlete.coach_id == coach.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.patch("/{athlete_id}", response_model=AthleteResponse)
def update_athlete(
    athlete_id: str,
    req: AthleteUpdate,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    athlete = (
        db.query(Athlete)
        .filter(Athlete.id == athlete_id, Athlete.coach_id == coach.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(athlete, key, value)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("/{athlete_id}/sessions", response_model=list[SessionResponse])
def list_athlete_sessions(
    athlete_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    athlete = (
        db.query(Athlete)
        .filter(Athlete.id == athlete_id, Athlete.coach_id == coach.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return (
        db.query(Session)
        .filter(Session.athlete_id == athlete_id)
        .order_by(Session.created_at.desc())
        .all()
    )


@router.get("/{athlete_id}/trends")
def get_athlete_trends(
    athlete_id: str,
    coach: Coach = Depends(get_current_coach),
    db: DBSession = Depends(get_db),
):
    """Return metric trends across all reviewed swings for this athlete."""
    athlete = (
        db.query(Athlete)
        .filter(Athlete.id == athlete_id, Athlete.coach_id == coach.id)
        .first()
    )
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    swings = (
        db.query(Swing)
        .join(Session)
        .filter(
            Session.athlete_id == athlete_id,
            Swing.status == SwingStatus.REVIEW_READY,
        )
        .order_by(Swing.created_at.asc())
        .all()
    )

    trend_data = []
    for swing in swings:
        ms = db.query(MetricSnapshot).filter(MetricSnapshot.swing_id == swing.id).first()
        interp = db.query(Interpretation).filter(Interpretation.swing_id == swing.id).first()
        if not ms:
            continue
        entry = {
            "swing_id": swing.id,
            "swing_type": swing.swing_type,
            "created_at": swing.created_at.isoformat() if swing.created_at else None,
            "metrics_contact": ms.metrics_json.get("contact", {}),
            "timing": ms.timing_json,
            "severity": interp.severity if interp else None,
        }
        trend_data.append(entry)

    return {"athlete_id": athlete_id, "swings": trend_data}
