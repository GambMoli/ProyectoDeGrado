from pathlib import Path
from types import SimpleNamespace

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.topic_explanation_service import TopicExplanationService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


def build_service() -> TopicExplanationService:
    settings = SimpleNamespace(rag_top_k=4)
    return TopicExplanationService(
        settings=settings,
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        ollama_client=None,
    )


def test_open_math_chat_returns_scope_message_without_corpus_match() -> None:
    service = build_service()

    result = service.answer("Hola, como estas")

    assert result.source == "math_scope_fallback"
    assert "calculo 1" in result.text.lower()
    assert result.references == []


def test_topic_explanation_uses_corpus_template_when_context_exists() -> None:
    service = build_service()

    result = service.answer("Explicame biseccion")

    assert result.source == "knowledge_template"
    assert result.references


def test_topic_explanation_accepts_conversation_context() -> None:
    service = build_service()

    result = service.answer(
        "Explicame derivacion implicita",
        conversation_context=["user: antes estabamos viendo derivadas"],
    )

    assert result.references


def test_course_overview_query_returns_outline_summary() -> None:
    service = build_service()

    result = service.answer("Que sabes de calculo 1")

    assert result.source == "course_outline_template"
    assert "funciones" in result.text.lower()
    assert "limites" in result.text.lower()
    assert "derivadas" in result.text.lower()
