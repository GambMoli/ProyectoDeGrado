from pathlib import Path
from types import SimpleNamespace

from app.schemas.enums import ChatMode
from app.services.conversation_planner_service import ConversationPlannerService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService

DATASETS_DIR = Path("/knowledge/datasets")
if not DATASETS_DIR.exists():
    DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


class FakePlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        prompt_lower = prompt.lower()
        if "dime que sabes de derivadas y proponme un ejercicio" in prompt_lower:
            return (
                '{"actions":["answer_theory","generate_practice"],'
                '"reason":"mixed_theory_practice","topic":"derivative","detail_level":"auto"}'
            )
        if "el resultado es 6x+2" in prompt_lower:
            return (
                '{"actions":["grade_practice"],'
                '"reason":"practice_attempt","topic":"derivative","detail_level":"auto"}'
            )
        return '{"actions":["ask_clarification"],"reason":"default","topic":null,"detail_level":"auto"}'


class BrokenPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return "salida invalida"


class HesitantPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return '{"actions":["ask_clarification"],"reason":"unsure","topic":null,"detail_level":"auto"}'


class MisleadingPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return '{"actions":["solve_exercise"],"reason":"wrong_router","topic":"integral","detail_level":"auto"}'


def build_service(ollama_client: object) -> ConversationPlannerService:
    return ConversationPlannerService(
        settings=SimpleNamespace(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
        parser_service=MathParserService(),
        ollama_client=ollama_client,  # type: ignore[arg-type]
    )


def test_planner_detects_mixed_theory_and_practice_request() -> None:
    service = build_service(FakePlannerOllamaClient())

    plan = service.plan(
        message="Dime que sabes de derivadas y proponme un ejercicio",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["answer_theory", "generate_practice"]
    assert plan.topic == "derivative"


def test_planner_detects_pending_practice_answer() -> None:
    service = build_service(FakePlannerOllamaClient())

    plan = service.plan(
        message="El resultado es 6x+2",
        requested_mode=ChatMode.AUTO,
        conversation_context=["assistant: Deriva la funcion f(x) = 3*x^2 + 2*x - 5."],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "expected_answer": "6*x + 2",
            }
        },
    )

    assert plan.actions == ["grade_practice"]


def test_planner_falls_back_to_rules_when_ollama_returns_invalid_output() -> None:
    service = build_service(BrokenPlannerOllamaClient())

    plan = service.plan(
        message="Dime que sabes de derivadas y proponme un ejercicio",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["answer_theory", "generate_practice"]


def test_planner_infers_course_level_practice_request_when_ollama_fails() -> None:
    service = build_service(BrokenPlannerOllamaClient())

    plan = service.plan(
        message="Asi esta bien, podrias darme un ejercicio de calculo 2",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["generate_practice"]


def test_planner_reroutes_ask_clarification_when_course_level_practice_is_clear() -> None:
    service = build_service(HesitantPlannerOllamaClient())

    plan = service.plan(
        message="Asi esta bien, podrias darme un ejercicio de calculo 2",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["generate_practice"]


def test_planner_reroutes_open_course_question_to_theory_when_llm_is_hesitant() -> None:
    service = build_service(HesitantPlannerOllamaClient())

    plan = service.plan(
        message="Hoola, que me puedes explicar de calculo 2",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["answer_theory"]


def test_planner_respects_requested_mode() -> None:
    service = build_service(BrokenPlannerOllamaClient())

    plan = service.plan(
        message="Resuelve x^2 + 1 = 0",
        requested_mode=ChatMode.EXERCISE,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["solve_exercise"]


def test_planner_reroutes_natural_practice_request_even_if_llm_marks_it_as_solver_task() -> None:
    service = build_service(MisleadingPlannerOllamaClient())

    plan = service.plan(
        message="Dame un ejercicio de integrales",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["generate_practice"]
    assert plan.reason == "guardrail_reroute_natural_practice_request"


def test_planner_keeps_solver_task_when_message_contains_explicit_math_expression() -> None:
    service = build_service(MisleadingPlannerOllamaClient())

    plan = service.plan(
        message="Resuelve la integral de x^2 + 1 dx",
        requested_mode=ChatMode.AUTO,
        conversation_context=[],
        agent_state={},
    )

    assert plan.actions == ["solve_exercise"]
