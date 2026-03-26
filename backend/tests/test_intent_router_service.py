from pathlib import Path

from app.schemas.enums import ChatMode
from app.services.intent_router_service import IntentRouterService
from app.services.knowledge_base_service import KnowledgeBaseService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


def build_router() -> IntentRouterService:
    return IntentRouterService(KnowledgeBaseService(DATASETS_DIR))


def test_router_detects_theory_query_with_corpus_context() -> None:
    router = build_router()

    intent = router.detect("Explicame que es el metodo de biseccion", requested_mode=ChatMode.AUTO)

    assert intent.mode == ChatMode.THEORY


def test_router_detects_exercise_query() -> None:
    router = build_router()

    intent = router.detect("Resuelve 2*x + 3 = 7", requested_mode=ChatMode.AUTO)

    assert intent.mode == ChatMode.EXERCISE


def test_router_respects_requested_mode() -> None:
    router = build_router()

    intent = router.detect("Resuelve 2*x + 3 = 7", requested_mode=ChatMode.THEORY)

    assert intent.mode == ChatMode.THEORY


def test_router_defaults_to_theory_for_open_chat() -> None:
    router = build_router()

    intent = router.detect("Hola, tengo una duda", requested_mode=ChatMode.AUTO)

    assert intent.mode == ChatMode.THEORY
