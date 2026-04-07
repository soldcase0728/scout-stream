from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    athlete_id: str
    session_type: str | None = None
    notes: str | None = None


class SessionResponse(BaseModel):
    id: str
    athlete_id: str
    coach_id: str
    session_type: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
