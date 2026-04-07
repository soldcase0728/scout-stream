import uuid

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    swing_id: Mapped[str] = mapped_column(String(36), ForeignKey("swings.id"), unique=True)

    metrics_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    deltas_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    timing_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    landmark_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    swing = relationship("Swing", back_populates="metric_snapshot")
