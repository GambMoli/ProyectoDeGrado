from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import app.services.conversation_service as conversation_service_module
from app.services.conversation_service import ConversationService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.topic_explanation_service import TopicExplanationService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        conversation_service_module,
        "get_settings",
        lambda: SimpleNamespace(max_upload_size_mb=5),
    )


def build_service() -> ConversationService:
    topic_explanation_service = TopicExplanationService(
        settings=SimpleNamespace(rag_top_k=4),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        ollama_client=None,
    )
    return ConversationService(
        repository=SimpleNamespace(),
        parser_service=MathParserService(),
        solver_service=SimpleNamespace(),
        explanation_service=SimpleNamespace(),
        ocr_service=SimpleNamespace(),
        practice_service=SimpleNamespace(),
        conversation_orchestrator_service=SimpleNamespace(),
        conversation_planner_service=SimpleNamespace(),
        response_composer_service=SimpleNamespace(),
        topic_explanation_service=topic_explanation_service,
    )


def test_scope_guard_rejects_clearly_off_topic_message() -> None:
    service = build_service()

    result = service._is_supported_text_message(
        message="Quien gano el partido de ayer en la liga?",
        conversation_context=[],
        agent_state={},
    )

    assert result is False


def test_scope_guard_accepts_math_question() -> None:
    service = build_service()

    result = service._is_supported_text_message(
        message="Explicame integracion por partes",
        conversation_context=[],
        agent_state={},
    )

    assert result is True


def test_scope_guard_accepts_contextual_follow_up_when_math_context_exists() -> None:
    service = build_service()

    result = service._is_supported_text_message(
        message="No entendi, puedes explicarme eso?",
        conversation_context=[
            "assistant: Vamos con un ejercicio para practicar. Calcula la integral de x*sin(x) dx."
        ],
        agent_state={
            "pending_practice": {
                "topic": "integral",
                "exercise_text": "Calcula la integral de x*sin(x) dx.",
            }
        },
    )

    assert result is True


def test_scope_guard_still_rejects_off_topic_message_even_with_math_context() -> None:
    service = build_service()

    result = service._is_supported_text_message(
        message="Cuentame algo de Shakira",
        conversation_context=[
            "assistant: Vamos con un ejercicio para practicar. Calcula la integral de x*sin(x) dx."
        ],
        agent_state={
            "pending_practice": {
                "topic": "integral",
                "exercise_text": "Calcula la integral de x*sin(x) dx.",
            }
        },
    )

    assert result is False


class FakeDirectReplyRepository:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def create_message(self, db: object, **kwargs: object) -> SimpleNamespace:
        kwargs.setdefault("error_message", None)
        return SimpleNamespace(
            id="assistant-message",
            created_at=datetime.now(timezone.utc),
            resolved_exercise=None,
            submitted_exercise=None,
            **kwargs,
        )

    def create_topic_metric_event(
        self,
        db: object,
        *,
        user_id: str,
        conversation_id: str,
        topic: str,
        interaction_type: str,
    ) -> None:
        self.events.append((topic, interaction_type))

    def touch_conversation(
        self,
        db: object,
        conversation: SimpleNamespace,
        *,
        summary: str | None = None,
        title_hint: str | None = None,
        agent_state: dict | None = None,
    ) -> None:
        conversation.summary = summary
        conversation.agent_state = agent_state or {}


def test_direct_reply_records_question_topic_without_generated_exercise_event() -> None:
    service = build_service()
    repository = FakeDirectReplyRepository()
    service.repository = repository  # type: ignore[assignment]
    conversation = SimpleNamespace(
        id="conversation-1",
        user_id="student-1",
        agent_state={"pending_practice": {"topic": "derivative"}},
        title="Nueva conversacion",
        summary=None,
    )
    user_message = SimpleNamespace(
        id="user-message",
        role="user",
        content="No entendi, puedes hacer el paso a paso?",
        source_type="text",
        status="received",
        error_message=None,
        created_at=datetime.now(timezone.utc),
        resolved_exercise=None,
        submitted_exercise=None,
    )

    response = service._respond_direct_text(
        db=object(),  # type: ignore[arg-type]
        user_id="student-1",
        conversation=conversation,  # type: ignore[arg-type]
        user_message=user_message,  # type: ignore[arg-type]
        assistant_text="Primero aplicamos la regla del producto.",
        raw_input=user_message.content,
        topic="derivative",
    )

    assert response.assistant_message.content == "Primero aplicamos la regla del producto."
    assert repository.events == [("derivative", "question")]
