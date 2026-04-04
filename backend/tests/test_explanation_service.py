from types import SimpleNamespace

from app.schemas.enums import ProblemType
from app.services.explanation_service import ExplanationService
from app.services.math_parser_service import ParsedExercise
from app.services.sympy_solver_service import SolvedExerciseData


class FakeOllamaClient:
    def generate(self, *, system_prompt: str, prompt: str, temperature: float = 0.2) -> str:
        return r"La idea clave es usar el limite notable \(\frac{\sin(x)}{x}\), y por eso el resultado es \(1\)."


def build_parsed_limit() -> ParsedExercise:
    return ParsedExercise(
        raw_input="Resuelve el limite cuando x tiende a 0 de sin(x)/x",
        problem_type=ProblemType.LIMIT,
        expression="sin(x)/x",
        variable="x",
        limit_point="0",
        notes=[],
    )


def build_solved_limit() -> SolvedExerciseData:
    return SolvedExerciseData(
        problem_type=ProblemType.LIMIT,
        sympy_input="Limit(sin(x)/x, x, 0)",
        final_result="1",
        steps=[
            r"Se identifica la expresion como \(\frac{\sin{\left(x \right)}}{x}\).",
            r"Evaluamos el limite cuando \(x \to 0\).",
            r"Analizamos el comportamiento de \(\frac{\sin{\left(x \right)}}{x}\) cerca de ese punto.",
            r"El valor del limite es \(1\).",
        ],
        variable="x",
    )


def test_explanation_service_uses_structured_fallback_for_plain_exercise_requests() -> None:
    service = ExplanationService(settings=SimpleNamespace(), ollama_client=FakeOllamaClient())

    result = service.generate(
        parsed=build_parsed_limit(),
        solved=build_solved_limit(),
        student_request="Resuelve el limite cuando x tiende a 0 de sin(x)/x",
    )

    assert result.source == "fallback"
    assert r"\(1\)" in result.text
    assert "Queremos calcular el limite" in result.text


def test_explanation_service_uses_llm_for_explicit_step_by_step_requests() -> None:
    service = ExplanationService(settings=SimpleNamespace(), ollama_client=FakeOllamaClient())

    result = service.generate(
        parsed=build_parsed_limit(),
        solved=build_solved_limit(),
        student_request="Explicame paso a paso este limite",
    )

    assert result.source == "ollama"
    assert r"\(\frac{\sin(x)}{x}\)" in result.text
