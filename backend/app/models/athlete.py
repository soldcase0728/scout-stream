import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.swing import Handedness, SwingType


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    coach_id: Mapped[str] = mapped_column(String(36), ForeignKey("coaches.id"))
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    handedness: Mapped[str] = mapped_column(Enum(Handedness), default=Handedness.RIGHT)
    primary_swing_type: Mapped[str] = mapped_column(
        Enum(SwingType), default=SwingType.REGULAR
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    coach = relationship("Coach", back_populates="athletes")
    sessions = relationship("Session", back_populates="athlete")
