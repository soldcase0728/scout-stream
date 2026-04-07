from pydantic import BaseModel


class SwingResponse(BaseModel):
    id: str
    session_id: str
    swing_type: str
    source_video_url: str
    processed_data_url: str | None
    status: str
    pipeline_version: str
    notes: str | None
    events: dict | None = None
    metrics: dict | None = None
    deltas: dict | None = None
    timing: dict | None = None
    interpretation: dict | None = None
    confidence: dict | None = None

    model_config = {"from_attributes": True}


class EventEditRequest(BaseModel):
    final_start_frame: int
    final_launch_frame: int
    final_contact_frame: int


class SwingNotesRequest(BaseModel):
    notes: str


class SwingUploadMeta(BaseModel):
    swing_type: str = "regular"
