from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.api.auth import get_current_coach
from app.schemas.athlete import AthleteCreate, AthleteUpdate, AthleteResponse

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
