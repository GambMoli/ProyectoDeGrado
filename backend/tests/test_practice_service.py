from pathlib import Path
from types import SimpleNamespace

from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.practice_service import PracticeService
from app.services.sympy_solver_service import SymPySolverService

DATASETS_DIR = Path("/knowledge/datasets")
if not DATASETS_DIR.exists():
    DATASETS_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "datasets"


def build_practice_service() -> PracticeService:
    return PracticeService(
        settings=SimpleNamespace(),
        parser_service=MathParserService(),
        solver_service=SymPySolverService(),
        ollama_client=None,
        knowledge_base_service=KnowledgeBaseService(DATASETS_DIR),
    )


def test_generate_derivative_practice_creates_pending_state() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    assert "Deriva la funcion" in generated.text
    assert generated.state["pending_practice"]["expected_answer"] == "6*x + 2"


def test_generate_taylor_practice_uses_requested_topic() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Dame un ejercicio de la serie de Taylor")

    assert "Taylor" in generated.text
    assert generated.state["pending_practice"]["topic"] == "serie_de_taylor"
    assert generated.state["pending_practice"]["expected_answer"] == "x**3/6 + x**2/2 + x + 1"


def test_generate_bisection_practice_uses_corpus_instead_of_derivative_default() -> None:
    service = build_practice_service()

    generated = service.generate_practice("Ponme un ejercicio de biseccion")

    assert "biseccion" in generated.text.lower()
    assert generated.state["pending_practice"]["topic"] == "biseccion"
    assert generated.state["pending_practice"]["grading_mode"] == "keyword_rubric"


def test_grade_correct_practice_attempt() -> None:
    service = build_practice_service()
    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    graded = service.grade_attempt(
        pending_practice=generated.state["pending_practice"],
        student_message="El resultado es 6x+2",
    )

    assert graded.is_correct is True
    assert graded.next_state == {}


def test_grade_incorrect_practice_attempt_keeps_state() -> None:
    service = build_practice_service()
    generated = service.generate_practice("Proponme un ejercicio de derivadas")

    graded = service.grade_attempt(
        pending_practice=generated.state["pending_practice"],
        student_message="El resultado es 5x+2",
    )

    assert graded.is_correct is False
    assert "pending_practice" in graded.next_state
