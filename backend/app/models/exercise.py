from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    assistant_message_id: Mapped[str | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_problem_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    extracted_expression: Mapped[str | None] = mapped_column(Text, nullable=True)
    variable: Mapped[str | None] = mapped_column(String(12), nullable=True)
    limit_point: Mapped[str | None] = mapped_column(String(48), nullable=True)
    parse_notes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="received")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    conversation = relationship("Conversation", back_populates="exercises")
    user_message = relationship(
        "Message",
        foreign_keys=[user_message_id],
        back_populates="submitted_exercise",
    )
    assistant_message = relationship(
        "Message",
        foreign_keys=[assistant_message_id],
        back_populates="resolved_exercise",
    )
    solved_exercise = relationship(
        "SolvedExercise",
        back_populates="exercise",
        uselist=False,
        cascade="all, delete-orphan",
    )
