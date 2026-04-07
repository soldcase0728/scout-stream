import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Handedness(str, enum.Enum):
    LEFT = "left"
    RIGHT = "right"


class SwingType(str, enum.Enum):
    REGULAR = "regular"
    LEFT_SLAP = "left_slap"
    POWER_SLAP = "power_slap"
    DRAG = "drag"
    BUNT = "bunt"


class SwingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    REVIEW_READY = "review_ready"
    FAILED = "failed"


class Swing(Base):
    __tablename__ = "swings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    swing_type: Mapped[str] = mapped_column(Enum(SwingType), default=SwingType.REGULAR)
    source_video_url: Mapped[str] = mapped_column(String(500))
    processed_data_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(Enum(SwingStatus), default=SwingStatus.UPLOADED)
    pipeline_version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="swings")
    event_review = relationship("EventReview", back_populates="swing", uselist=False)
    metric_snapshot = relationship("MetricSnapshot", back_populates="swing", uselist=False)
    interpretation = relationship("Interpretation", back_populates="swing", uselist=False)
