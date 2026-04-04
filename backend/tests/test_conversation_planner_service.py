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
                '{"intent":"mixed_theory_practice","target":"new_topic",'
                '"reason":"mixed_theory_practice","topic":"derivative","detail_level":"auto","confidence":0.96}'
            )
        if "el resultado es 6x+2" in prompt_lower:
            return (
                '{"intent":"grade_active_practice","target":"active_practice",'
                '"reason":"practice_attempt","topic":"derivative","detail_level":"auto","confidence":0.9}'
            )
        if "puedes explicarme ese ejercicio paso por paso" in prompt_lower:
            return (
                '{"intent":"explain_practice_context","target":"active_practice",'
                '"reason":"walk_through_pending","topic":"integral","detail_level":"detailed","confidence":0.94}'
            )
        if "si, dame el paso a paso" in prompt_lower:
            return (
                '{"intent":"explain_practice_context","target":"recent_practice",'
                '"reason":"continue_recent_exercise","topic":"integral","detail_level":"detailed","confidence":0.91}'
            )
        return '{"intent":"clarify","target":"unknown","reason":"default","topic":null,"detail_level":"auto","confidence":0.3}'


class BrokenPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return "salida invalida"


class HesitantPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return '{"intent":"clarify","target":"unknown","reason":"unsure","topic":null,"detail_level":"auto","confidence":0.2}'


class MisleadingPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return '{"intent":"solve_new_problem","target":"new_problem","reason":"wrong_router","topic":"integral","detail_level":"auto","confidence":0.72}'


class PracticeRecoveryPlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        prompt_lower = prompt.lower()
        if "continuaciones de una practica matematica" in prompt_lower and "si, dame el paso a paso" in prompt_lower:
            return (
                '{"actions":["explain_practice_context"],"reason":"continue_recent_exercise",'
                '"topic":"integral","detail_level":"detailed"}'
            )
        return '{"intent":"clarify","target":"unknown","reason":"unsure","topic":null,"detail_level":"auto","confidence":0.2}'


class ContextAwarePracticePlannerOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        prompt_lower = prompt.lower()
        if "resolutor semantico del contexto de practica" in prompt_lower:
            if "no supe resolverlo, podrias hacerme el paso por paso?" in prompt_lower:
                return (
                    '{"actions":["explain_practice_context"],"reason":"needs_help_with_current_exercise",'
                    '"topic":"derivative","detail_level":"detailed","confidence":0.94}'
                )
            if "el ejercicio anterior no lo supe resolver, dame el paso por paso." in prompt_lower:
                return (
                    '{"actions":["explain_practice_context"],"reason":"revisit_previous_exercise",'
                    '"topic":"derivative","detail_level":"detailed","confidence":0.92}'
                )
        return '{"intent":"clarify","target":"unknown","reason":"default","topic":null,"detail_level":"auto","confidence":0.3}'


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


def test_planner_detects_request_to_explain_active_practice() -> None:
    service = build_service(FakePlannerOllamaClient())

    plan = service.plan(
        message="Puedes explicarme ese ejercicio paso por paso?",
        requested_mode=ChatMode.AUTO,
        conversation_context=["assistant: Resuelve esta integral: integral de x^2 + 4*x + 1 dx."],
        agent_state={
            "pending_practice": {
                "topic": "integral",
                "exercise_text": "Resuelve esta integral: integral de x^2 + 4*x + 1 dx.",
            }
        },
    )

    assert plan.actions == ["explain_practice_context"]
    assert plan.detail_level == "detailed"


def test_planner_detects_request_to_explain_recently_completed_practice() -> None:
    service = build_service(FakePlannerOllamaClient())

    plan = service.plan(
        message="Si, dame el paso a paso",
        requested_mode=ChatMode.AUTO,
        conversation_context=[
            "assistant: Si, ese resultado esta correcto: -x*cos(x) + sin(x). "
            "Si quieres, ahora revisamos el procedimiento paso a paso o te propongo uno un poco mas retador."
        ],
        agent_state={
            "last_practice_context": {
                "topic": "integral",
                "exercise_text": "Resuelve la integral de x*sin(x) dx usando integracion por partes.",
                "expected_answer": "-x*cos(x) + sin(x)",
                "status": "completed",
                "last_outcome": "correct",
            }
        },
    )

    assert plan.actions == ["explain_practice_context"]
    assert plan.detail_level == "detailed"


def test_planner_recovers_recent_practice_follow_up_semantically() -> None:
    service = build_service(PracticeRecoveryPlannerOllamaClient())

    plan = service.plan(
        message="Si, dame el paso a paso",
        requested_mode=ChatMode.AUTO,
        conversation_context=[
            "assistant: Si, ese resultado esta correcto: -x*cos(x) + sin(x). "
            "Si quieres, ahora revisamos el procedimiento paso a paso o te propongo uno un poco mas retador."
        ],
        agent_state={
            "last_practice_context": {
                "topic": "integral",
                "exercise_text": "Resuelve la integral de x*sin(x) dx usando integracion por partes.",
                "expected_answer": "-x*cos(x) + sin(x)",
                "status": "completed",
                "last_outcome": "correct",
            }
        },
    )

    assert plan.actions == ["explain_practice_context"]
    assert plan.reason.startswith("practice_follow_up_")


def test_planner_understands_help_request_for_active_practice_from_contextual_step() -> None:
    service = build_service(ContextAwarePracticePlannerOllamaClient())

    plan = service.plan(
        message="No supe resolverlo, podrias hacerme el paso por paso?",
        requested_mode=ChatMode.AUTO,
        conversation_context=[
            "assistant: Vamos con un ejercicio para practicar. Calcula la derivada de x^2*cos(x)."
        ],
        agent_state={
            "pending_practice": {
                "topic": "derivative",
                "exercise_text": "Calcula la derivada de x^2*cos(x).",
                "expected_answer": "-x^2*sin(x) + 2*x*cos(x)",
            }
        },
    )

    assert plan.actions == ["explain_practice_context"]
    assert plan.reason.startswith("contextual_practice_")


def test_planner_understands_help_request_for_recent_practice_from_contextual_step() -> None:
    service = build_service(ContextAwarePracticePlannerOllamaClient())

    plan = service.plan(
        message="El ejercicio anterior no lo supe resolver, dame el paso por paso.",
        requested_mode=ChatMode.AUTO,
        conversation_context=[
            "assistant: Hace un momento te propuse derivar x*cos(x)."
        ],
        agent_state={
            "last_practice_context": {
                "topic": "derivative",
                "exercise_text": "Calcula la derivada de x*cos(x).",
                "expected_answer": "-x*sin(x) + cos(x)",
                "status": "completed",
                "last_outcome": "incorrect",
            }
        },
    )

    assert plan.actions == ["explain_practice_context"]
    assert plan.reason.startswith("contextual_practice_")


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
