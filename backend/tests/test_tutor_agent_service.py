from pathlib import Path
from types import SimpleNamespace

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.tutor_agent_service import TutorAgentService

DATASETS_DIR = Path("/knowledge/datasets")
if not DATASETS_DIR.exists():
    DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


def build_agent() -> TutorAgentService:
    return TutorAgentService(
        settings=SimpleNamespace(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        parser_service=MathParserService(),
        ollama_client=None,
    )


def test_agent_detects_practice_request() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Proponme un ejercicio de derivadas",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "generate_practice"
    assert decision.topic == "derivative"


def test_agent_detects_taylor_practice_request() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Dame un ejercicio de la serie de Taylor",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "generate_practice"
    assert decision.topic == "serie_de_taylor"


def test_agent_detects_practice_answer_when_pending() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="El resultado es 6x+2",
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert decision.action == "grade_practice"


def test_agent_detects_practice_topic_correction() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Repito, eso es de derivada, no de la serie de Taylor",
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert decision.action == "generate_practice"
    assert decision.topic == "serie_de_taylor"


def test_agent_detects_theory_question() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Que sabes de calculo 1",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "answer_theory"
