from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.topic_explanation_service import TopicExplanationService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


class FakeOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        if "Esquema del curso:" in prompt:
            return "Calculo 1 cubre funciones, limites y derivadas. Puedes profundizar en cualquiera de esos bloques."
        if "Contexto recuperado del corpus:" in prompt:
            return "Biseccion usa un intervalo con cambio de signo y lo divide repetidamente para acercarse a la raiz."
        return (
            "Entiendo que estas listo para empezar nuestra conversacion sobre calculo y metodos numericos. "
            "Sin embargo, no tengo registro de ningun contexto previo o tema especifico que debamos discutir. "
            "Podrias comenzar por decirme que te gustaria hablar o explorar en este espacio? "
            "Estoy aqui para ayudarte y apoyarte en tu aprendizaje."
        )


def build_service() -> TopicExplanationService:
    settings = SimpleNamespace(rag_top_k=4)
    return TopicExplanationService(
        settings=settings,
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        ollama_client=FakeOllamaClient(),
    )


def test_open_math_chat_returns_scope_message_without_corpus_match() -> None:
    service = build_service()

    result = service.answer("Hola, como estas")

    assert result.source == "ollama_math_chat"
    assert result.references == []
    assert result.text == (
        "Puedo ayudarte con calculo y metodos numericos. "
        "Dime que tema, metodo o ejercicio quieres revisar y lo vemos paso a paso."
    )


def test_topic_explanation_uses_corpus_template_when_context_exists() -> None:
    service = build_service()

    result = service.answer("Explicame biseccion")

    assert result.source == "ollama_rag"
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

    assert result.source == "ollama_course_overview"
    assert "funciones" in result.text.lower()
    assert "limites" in result.text.lower()
    assert "derivadas" in result.text.lower()


def test_open_course_question_is_treated_as_course_overview() -> None:
    service = build_service()

    result = service.answer("Que me puedes explicar de calculo 1")

    assert result.source == "ollama_course_overview"
    assert "funciones" in result.text.lower()


def test_topic_explanation_requires_ollama() -> None:
    service = TopicExplanationService(
        settings=SimpleNamespace(rag_top_k=4),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        ollama_client=None,
    )

    with pytest.raises(RuntimeError, match="OllamaClient no esta configurado"):
        service.answer("Explicame biseccion")


def test_normalize_llm_text_keeps_natural_math_explanation() -> None:
    text = "La derivada mide la tasa de cambio instantanea de una funcion."

    normalized = TopicExplanationService._normalize_llm_text(text)

    assert normalized == text
