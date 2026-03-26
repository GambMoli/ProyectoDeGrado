from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation import Conversation
from app.models.exercise import Exercise
from app.models.message import Message
from app.models.solved_exercise import SolvedExercise
from app.models.user import User

_UNSET = object()


class ConversationRepository:
    def get_or_create_user(self, db: Session, user_id: str | None) -> User:
        if user_id:
            user = db.get(User, user_id)
            if user:
                return user

            user = User(
                id=user_id,
                display_name=f"Estudiante {user_id[:8]}",
                is_anonymous=True,
            )
            db.add(user)
            db.flush()
            return user

        generated_user = User(
            display_name=f"Estudiante {uuid4().hex[:6]}",
            is_anonymous=True,
        )
        db.add(generated_user)
        db.flush()
        return generated_user

    def get_or_create_conversation(
        self,
        db: Session,
        user_id: str,
        conversation_id: str | None,
        title_hint: str | None,
    ) -> Conversation:
        if conversation_id:
            conversation = db.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise LookupError("La conversacion no existe para este usuario.")
            return conversation

        conversation = Conversation(
            user_id=user_id,
            title=self._build_title(title_hint),
            agent_state={},
        )
        db.add(conversation)
        db.flush()
        return conversation

    def create_message(
        self,
        db: Session,
        *,
        conversation_id: str,
        role: str,
        content: str,
        source_type: str | None,
        status: str,
        error_message: str | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            source_type=source_type,
            status=status,
            error_message=error_message,
        )
        db.add(message)
        db.flush()
        return message

    def create_exercise(
        self,
        db: Session,
        *,
        conversation_id: str,
        user_message_id: str,
        source_type: str,
        raw_input: str,
        ocr_text: str | None = None,
    ) -> Exercise:
        exercise = Exercise(
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            source_type=source_type,
            raw_input=raw_input,
            ocr_text=ocr_text,
        )
        db.add(exercise)
        db.flush()
        return exercise

    def create_solved_exercise(
        self,
        db: Session,
        *,
        exercise_id: str,
        sympy_input: str,
        final_result: str,
        steps: list[str],
        explanation_text: str,
        explanation_source: str,
    ) -> SolvedExercise:
        solved = SolvedExercise(
            exercise_id=exercise_id,
            sympy_input=sympy_input,
            final_result=final_result,
            steps_json=steps,
            explanation_text=explanation_text,
            explanation_source=explanation_source,
        )
        db.add(solved)
        db.flush()
        return solved

    def touch_conversation(
        self,
        db: Session,
        conversation: Conversation,
        *,
        summary: str | None = None,
        title_hint: str | None = None,
        agent_state: dict | None | object = _UNSET,
    ) -> Conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        if summary:
            conversation.summary = summary[:400]
        if title_hint and conversation.title == "Nueva conversacion":
            conversation.title = self._build_title(title_hint)
        if agent_state is not _UNSET:
            conversation.agent_state = agent_state or {}
        db.add(conversation)
        db.flush()
        return conversation

    def list_conversations(self, db: Session, user_id: str | None) -> list[Conversation]:
        if not user_id:
            return []

        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.updated_at.desc())
        )
        return list(db.scalars(query).unique().all())

    def get_conversation(
        self,
        db: Session,
        conversation_id: str,
        user_id: str | None = None,
    ) -> Conversation | None:
        query: Select[tuple[Conversation]] = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(
                selectinload(Conversation.messages)
                .selectinload(Message.submitted_exercise)
                .selectinload(Exercise.solved_exercise),
                selectinload(Conversation.messages)
                .selectinload(Message.resolved_exercise)
                .selectinload(Exercise.solved_exercise),
            )
        )

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        return db.scalars(query).unique().first()

    @staticmethod
    def _build_title(seed: str | None) -> str:
        if not seed:
            return "Nueva conversacion"

        cleaned = " ".join(seed.strip().split())
        if not cleaned:
            return "Nueva conversacion"
        return cleaned[:70]
