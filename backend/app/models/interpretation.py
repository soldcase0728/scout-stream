import enum
import uuid

from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Severity(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Interpretation(Base):
    __tablename__ = "interpretations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    swing_id: Mapped[str] = mapped_column(String(36), ForeignKey("swings.id"), unique=True)

    what_happened: Mapped[str] = mapped_column(Text)
    what_it_means: Mapped[str] = mapped_column(Text)
    what_to_coach_next: Mapped[str] = mapped_column(Text)
    rules_triggered: Mapped[dict] = mapped_column(JSONB, default=list)
    severity: Mapped[str] = mapped_column(Enum(Severity), default=Severity.LOW)

    swing = relationship("Swing", back_populates="interpretation")
