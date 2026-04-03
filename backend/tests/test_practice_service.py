from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.ollama_client import OllamaClientError
from app.services.practice_service import PracticeService
from app.services.sympy_solver_service import SymPySolverService

DATASETS_DIR = Path("/knowledge/datasets")
if not DATASETS_DIR.exists():
    DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


class FakeOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        prompt_lower = prompt.lower()
        if "Devuelves solo JSON valido" in system_prompt and "generador interno de practica matematica" in system_prompt:
            if "serie de taylor" in prompt_lower:
                return (
                    '{"mode":"taylor","function_expr":"sin(x)","center":"0","order":4,'
                    '"exercise_text":"Construye el polinomio de Taylor de orden 4 de sin(x) alrededor de x = 0.",'
                    '"hint":"Alterna derivadas de sin y cos, y conserva solo hasta grado 4."}'
                )
            if "biseccion" in prompt_lower:
                return (
                    '{"exercise_text":"Explica el metodo de biseccion y menciona una condicion necesaria para aplicarlo.",'
                    '"expected_answer":"Se necesita un intervalo con cambio de signo y continuidad para aplicar biseccion.",'
                    '"hint":"Piensa en cambio de signo y continuidad.",'
                    '"rubric":"Debe mencionar intervalo con cambio de signo y continuidad.",'
                    '"keywords":["intervalo","signo","continuidad","biseccion"]}'
                )
            if "objetivo matematico:" in prompt_lower and "derivadas" in prompt_lower:
                return (
                    '{"mode":"symbolic","raw_input":"derivada de 5*x^2 - 4*x + 1",'
                    '"exercise_text":"Deriva la funcion f(x) = 5*x^2 - 4*x + 1.",'
                    '"hint":"Aplica la regla de la potencia termino a termino."}'
                )
            return (
                '{"exercise_text":"Explica el tema recuperado y su utilidad.",'
                '"expected_answer":"Respuesta breve sobre el tema.",'
                '"hint":"Describe que es y para que sirve.",'
                '"rubric":"Debe explicar la idea central.",'
                '"keywords":["tema","utilidad"]}'
            )
        if "Eres un tutor matematico cercano y preciso." in system_prompt:
            return "Hay un error en tu respuesta. Revisa la pista y vuelve a intentarlo."
        if "evaluador interno de practica matematica" in system_prompt:
            return '{"is_correct": false, "feedback": "La respuesta aun no cubre la idea principal."}'
        return "Salida de prueba de Ollama."


def build_practice_service() -> PracticeService:
    return PracticeService(
        settings=SimpleNamespace(),
        parser_service=MathParserService(),
        solver_service=SymPySolverService(),
        ollama_client=FakeOllamaClient(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
    )


class TimeoutFeedbackOllamaClient(FakeOllamaClient):
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        if "Eres un tutor matematico cercano y preciso." in system_prompt:
            raise OllamaClientError("timeout")
        return super().generate(system_prompt=system_prompt, prompt=prompt, temperature=temperature)


def test_generate_derivative_practice_creates_pending_state() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    assert "Deriva la funcion" in generated.text
    assert generated.state["pending_practice"]["expected_answer"] == "10*x - 4"
    assert generated.state["practice_history"]


def test_generate_taylor_practice_uses_requested_topic() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Dame un ejercicio de la serie de Taylor")

    assert "Taylor" in generated.text
    assert generated.state["pending_practice"]["topic"] == "serie_de_taylor"
    assert generated.state["pending_practice"]["expected_answer"] == "-x**3/6 + x"


def test_generate_bisection_practice_uses_corpus_instead_of_derivative_default() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Ponme un ejercicio de biseccion")

    assert "biseccion" in generated.text.lower()
    assert generated.state["pending_practice"]["topic"] == "biseccion"
    assert generated.state["pending_practice"]["grading_mode"] == "llm_rubric"


def test_grade_correct_practice_attempt() -> None:
    service = build_practice_service()
    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    graded = service.grade_attempt(
        pending_practice=generated.state["pending_practice"],
        student_message="El resultado es 10x-4",
    )

    assert graded.is_correct is True
    assert "pending_practice" not in graded.next_state
    assert graded.next_state["practice_history"]


def test_grade_incorrect_practice_attempt_keeps_state() -> None:
    service = build_practice_service()
    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    graded = service.grade_attempt(
        pending_practice=generated.state["pending_practice"],
        student_message="El resultado es 5x+2",
    )

    assert graded.is_correct is False
    assert "pending_practice" in graded.next_state


def test_integral_practice_accepts_equivalent_answer_with_constant() -> None:
    service = build_practice_service()

    pending_practice = {
        "problem_type": "integral",
        "expected_answer": "x**3/3 + 2*x**2 + x",
        "exercise_text": "Resuelve esta integral.",
        "hint": "Integra termino a termino.",
        "practice_history": [],
        "attempts": 0,
    }

    graded = service.grade_attempt(
        pending_practice=pending_practice,
        student_message="x^3/3 + 2x^2 + x + C",
    )

    assert graded.is_correct is True


def test_grade_incorrect_practice_attempt_uses_fallback_when_ollama_times_out() -> None:
    service = PracticeService(
        settings=SimpleNamespace(),
        parser_service=MathParserService(),
        solver_service=SymPySolverService(),
        ollama_client=TimeoutFeedbackOllamaClient(),
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
    )
    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    graded = service.grade_attempt(
        pending_practice=generated.state["pending_practice"],
        student_message="El resultado es 5x+2",
    )

    assert graded.is_correct is False
    assert "No coincide todavia" in graded.text


def test_practice_service_requires_ollama() -> None:
    service = PracticeService(
        settings=SimpleNamespace(),
        parser_service=MathParserService(),
        solver_service=SymPySolverService(),
        ollama_client=None,
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
    )

    with pytest.raises(RuntimeError, match="OllamaClient no esta configurado"):
        service.generate_practice("Proponme un ejercicio de derivadas")
