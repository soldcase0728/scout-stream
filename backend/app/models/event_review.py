import uuid

from sqlalchemy import String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventReview(Base):
    __tablename__ = "event_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    swing_id: Mapped[str] = mapped_column(String(36), ForeignKey("swings.id"), unique=True)

    auto_start_frame: Mapped[int] = mapped_column(Integer)
    auto_launch_frame: Mapped[int] = mapped_column(Integer)
    auto_contact_frame: Mapped[int] = mapped_column(Integer)

    final_start_frame: Mapped[int] = mapped_column(Integer)
    final_launch_frame: Mapped[int] = mapped_column(Integer)
    final_contact_frame: Mapped[int] = mapped_column(Integer)

    manual_override: Mapped[bool] = mapped_column(Boolean, default=False)
    event_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    swing = relationship("Swing", back_populates="event_review")
