from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SolvedExercise(Base):
    __tablename__ = "solved_exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    exercise_id: Mapped[str] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    sympy_input: Mapped[str] = mapped_column(Text, nullable=False)
    final_result: Mapped[str] = mapped_column(Text, nullable=False)
    steps_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_source: Mapped[str] = mapped_column(String(30), nullable=False, default="template")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    exercise = relationship("Exercise", back_populates="solved_exercise")
