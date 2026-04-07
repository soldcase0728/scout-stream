import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id: Mapped[str] = mapped_column(String(36), ForeignKey("athletes.id"))
    coach_id: Mapped[str] = mapped_column(String(36), ForeignKey("coaches.id"))
    session_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    athlete = relationship("Athlete", back_populates="sessions")
    coach = relationship("Coach", back_populates="sessions")
    swings = relationship("Swing", back_populates="session")
