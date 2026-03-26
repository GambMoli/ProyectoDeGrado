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


def test_parser_detects_equation_and_solver_resolves_it() -> None:
    parser = MathParserService()
    solver = SymPySolverService()

    parsed = parser.parse("Resuelve 2*x + 3 = 7")
    solved = solver.solve(parsed)

    assert parsed.problem_type == ProblemType.EQUATION
    assert solved.final_result == "x = 2"
