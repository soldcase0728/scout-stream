from datetime import datetime

from pydantic import BaseModel


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    handedness: str = "right"
    primary_swing_type: str = "regular"
    notes: str | None = None


class AthleteUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    handedness: str | None = None
    primary_swing_type: str | None = None
    notes: str | None = None


class AthleteResponse(BaseModel):
    id: str
    coach_id: str
    first_name: str
    last_name: str
    handedness: str
    primary_swing_type: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
