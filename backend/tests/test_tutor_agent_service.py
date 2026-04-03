from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.tutor_agent_service import TutorAgentService

DATASETS_DIR = Path("/knowledge/datasets")
if not DATASETS_DIR.exists():
    DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


class FakeOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        prompt_lower = prompt.lower()
        if "proponme un ejercicio de derivadas" in prompt_lower:
            return '{"action":"generate_practice","reason":"practice_request","topic":"derivative"}'
        if "dame un ejercicio de la serie de taylor" in prompt_lower:
            return '{"action":"generate_practice","reason":"practice_request","topic":"serie_de_taylor"}'
        if "el resultado es 6x+2" in prompt_lower:
            return '{"action":"grade_practice","reason":"pending_practice_attempt","topic":"derivative"}'
        if "repito, eso es de derivada, no de la serie de taylor" in prompt_lower:
            return '{"action":"generate_practice","reason":"practice_topic_correction","topic":"serie_de_taylor"}'
        if "que sabes de calculo 1" in prompt_lower:
            return '{"action":"answer_theory","reason":"theory_query","topic":"calculo_1"}'
        return '{"action":"ask_clarification","reason":"default","topic":null}'


class BrokenOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return "respuesta invalida"


def build_agent() -> TutorAgentService:
    return TutorAgentService(
        settings=SimpleNamespace(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        parser_service=MathParserService(),
        ollama_client=FakeOllamaClient(),
    )


def build_broken_agent() -> TutorAgentService:
    return TutorAgentService(
        settings=SimpleNamespace(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        parser_service=MathParserService(),
        ollama_client=BrokenOllamaClient(),
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


def test_agent_detects_mixed_theory_and_practice_request() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Dime que sabes de derivadas y proponme un ejercicio",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "answer_theory_with_practice"


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


def test_agent_detects_short_math_answer_when_it_matches_pending_practice() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="6x+2",
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


def test_agent_allows_context_switch_to_new_exercise_when_practice_is_pending() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Resuelve x^2 + 3*x = 10",
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert decision.action == "solve_exercise"


def test_agent_allows_mixed_theory_and_practice_when_practice_is_pending() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Explicame que es una derivada y proponme un ejercicio",
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert decision.action == "answer_theory_with_practice"


def test_agent_does_not_force_practice_grading_for_unrelated_math_expression() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="x^3/3 + 2x^2 + x + C",
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert decision.action == "solve_exercise"


def test_agent_detects_theory_question() -> None:
    agent = build_agent()

    decision = agent.decide(
        message="Que sabes de calculo 1",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "answer_theory"


def test_agent_falls_back_to_rules_when_ollama_returns_invalid_router_output() -> None:
    agent = build_broken_agent()

    decision = agent.decide(
        message="Dime que sabes de derivadas y proponme un ejercicio",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "answer_theory_with_practice"


def test_agent_falls_back_to_rule_based_theory_routing() -> None:
    agent = build_broken_agent()

    decision = agent.decide(
        message="Que es una derivada",
        conversation_context=[],
        agent_state={},
    )

    assert decision.action == "answer_theory"


def test_agent_requires_ollama() -> None:
    agent = TutorAgentService(
        settings=SimpleNamespace(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        parser_service=MathParserService(),
        ollama_client=None,
    )

    with pytest.raises(RuntimeError, match="OllamaClient no esta configurado"):
        agent.decide(message="Que sabes de calculo 1", conversation_context=[], agent_state={})
