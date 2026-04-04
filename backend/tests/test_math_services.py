from app.schemas.enums import ProblemType
from app.services.math_parser_service import MathParserService
from app.services.sympy_solver_service import SymPySolverService


def test_parser_detects_derivative_and_solver_resolves_it() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Explicame paso a paso esta derivada: derivada de x^3")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.DERIVATIVE
    assert parsed.expression == "x^3"
    assert solved.final_result == "3*x**2"


def test_parser_detects_integral_and_solver_resolves_it() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Integral de x^2 dx")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.INTEGRAL
    assert solved.final_result == "x**3/3"


def test_parser_detects_unicode_integral_symbol() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("∫ x^2 dx")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.INTEGRAL
    assert solved.final_result == "x**3/3"


def test_parser_detects_equation_and_solver_resolves_it() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Resuelve 2*x + 3 = 7")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.EQUATION
    assert solved.final_result == "x = 2"


def test_parser_detects_limit_with_textual_context_and_cleans_expression() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Resuelve el limite cuando x tiende a 0 de sin(x)/x^5")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.LIMIT
    assert parsed.expression == "sin(x)/x^5"
    assert parsed.variable == "x"
    assert parsed.limit_point == "0"
    assert solved.final_result == "oo"


def test_parser_detects_limit_without_literal_keyword_if_context_is_clear() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Resuelve 3 sin(x) / x^5 cuando x tiende a 0")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.LIMIT
    assert parsed.expression == "3 sin(x) / x^5"
    assert parsed.variable == "x"
    assert parsed.limit_point == "0"
    assert solved.final_result == "oo"


def test_parser_prefers_math_line_from_multiline_limit_prompt() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Resuelve el limite cuando x tiende a 0:\nsin(x)/x^5")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.LIMIT
    assert parsed.expression == "sin(x)/x^5"
    assert parsed.limit_point == "0"
    assert solved.final_result == "oo"


def test_parser_discards_ocr_like_instruction_letters_before_limit_expression() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("R l s u v e 3 sin(x) / x^5 cuando x tiende a 0")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.LIMIT
    assert parsed.expression == "3 sin(x) / x^5"
    assert parsed.limit_point == "0"
    assert solved.final_result == "oo"
