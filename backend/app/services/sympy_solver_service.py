from __future__ import annotations

from dataclasses import dataclass

from sympy import E, Derivative, Eq, Integral, Limit, Symbol, cos, diff, exp, integrate, latex, limit, log, pi
from sympy import simplify, sin, solve, sqrt, tan
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.schemas.enums import ProblemType
from app.services.math_parser_service import ParsedExercise


class SolverError(ValueError):
    def __init__(self, user_message: str) -> None:
        super().__init__(user_message)
        self.user_message = user_message


@dataclass(slots=True)
class SolvedExerciseData:
    problem_type: ProblemType
    sympy_input: str
    final_result: str
    steps: list[str]
    variable: str | None = None


class SymPySolverService:
    _transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    def __init__(self) -> None:
        symbol_names = "x y z t n a b c"
        self.local_dict = {name: Symbol(name) for name in symbol_names.split()}
        self.local_dict.update(
            {
                "sin": sin,
                "cos": cos,
                "tan": tan,
                "ln": log,
                "log": log,
                "exp": exp,
                "sqrt": sqrt,
                "pi": pi,
                "e": E,
            }
        )

    def solve(self, parsed: ParsedExercise) -> SolvedExerciseData:
        try:
            if parsed.problem_type == ProblemType.DERIVATIVE:
                return self._solve_derivative(parsed)
            if parsed.problem_type == ProblemType.INTEGRAL:
                return self._solve_integral(parsed)
            if parsed.problem_type == ProblemType.LIMIT:
                return self._solve_limit(parsed)
            if parsed.problem_type == ProblemType.EQUATION:
                return self._solve_equation(parsed)
            return self._solve_simplification(parsed)
        except SolverError:
            raise
        except Exception as exc:
            raise SolverError(
                "No pude resolver ese ejercicio todavia. Prueba con una expresion mas simple o revisa el formato."
            ) from exc

    def _solve_derivative(self, parsed: ParsedExercise) -> SolvedExerciseData:
        expr = self._parse_expression(parsed.expression)
        variable = self._resolve_symbol(parsed.variable, [expr])
        result = simplify(diff(expr, variable))
        return SolvedExerciseData(
            problem_type=parsed.problem_type,
            sympy_input=str(Derivative(expr, variable)),
            final_result=str(result),
            variable=str(variable),
            steps=[
                f"Se identifica la funcion como \\({self._to_latex(expr)}\\).",
                f"La variable de derivacion es \\({self._to_latex(variable)}\\).",
                f"Aplicamos la derivada con respecto a \\({self._to_latex(variable)}\\).",
                f"El resultado obtenido es \\({self._to_latex(result)}\\).",
            ],
        )

    def _solve_integral(self, parsed: ParsedExercise) -> SolvedExerciseData:
        expr = self._parse_expression(parsed.expression)
        variable = self._resolve_symbol(parsed.variable, [expr])
        result = simplify(integrate(expr, variable))
        return SolvedExerciseData(
            problem_type=parsed.problem_type,
            sympy_input=str(Integral(expr, variable)),
            final_result=str(result),
            variable=str(variable),
            steps=[
                f"Se identifica el integrando como \\({self._to_latex(expr)}\\).",
                f"La variable de integracion es \\({self._to_latex(variable)}\\).",
                f"Buscamos una antiderivada respecto de \\({self._to_latex(variable)}\\).",
                f"Una antiderivada es \\({self._to_latex(result)}\\).",
            ],
        )

    def _solve_limit(self, parsed: ParsedExercise) -> SolvedExerciseData:
        expr = self._parse_expression(parsed.expression)
        variable = self._resolve_symbol(parsed.variable, [expr])
        if not parsed.limit_point:
            raise SolverError("El limite necesita un punto de evaluacion.")

        point = self._parse_expression(parsed.limit_point)
        result = simplify(limit(expr, variable, point))
        return SolvedExerciseData(
            problem_type=parsed.problem_type,
            sympy_input=str(Limit(expr, variable, point)),
            final_result=str(result),
            variable=str(variable),
            steps=[
                f"Se identifica la expresion como \\({self._to_latex(expr)}\\).",
                f"Evaluamos el limite cuando \\({self._to_latex(variable)} \\to {self._to_latex(point)}\\).",
                f"Analizamos el comportamiento de \\({self._to_latex(expr)}\\) cerca de ese punto.",
                f"El valor del limite es \\({self._to_latex(result)}\\).",
            ],
        )

    def _solve_equation(self, parsed: ParsedExercise) -> SolvedExerciseData:
        if "=" not in parsed.expression:
            raise SolverError(
                "Para resolver una ecuacion necesito un formato con signo igual, por ejemplo 2*x + 3 = 7."
            )

        left_raw, right_raw = parsed.expression.split("=", maxsplit=1)
        left_expr = self._parse_expression(left_raw)
        right_expr = self._parse_expression(right_raw)
        variable = self._resolve_symbol(parsed.variable, [left_expr, right_expr])
        solutions = solve(Eq(left_expr, right_expr), variable)
        if not solutions:
            final_result = "No se encontraron soluciones simbolicas."
        elif len(solutions) == 1:
            final_result = f"{variable} = {solutions[0]}"
        else:
            formatted = ", ".join(str(solution) for solution in solutions)
            final_result = f"{variable} ∈ {{{formatted}}}"

        return SolvedExerciseData(
            problem_type=parsed.problem_type,
            sympy_input=str(Eq(left_expr, right_expr)),
            final_result=final_result,
            variable=str(variable),
            steps=[
                f"Se identifica la ecuacion como \\({self._to_latex(left_expr)} = {self._to_latex(right_expr)}\\).",
                f"La variable a despejar es \\({self._to_latex(variable)}\\).",
                "Aplicamos despeje simbolico para encontrar los valores que satisfacen la igualdad.",
                f"Las soluciones encontradas fueron \\({self._to_latex_text(final_result)}\\).",
            ],
        )

    def _solve_simplification(self, parsed: ParsedExercise) -> SolvedExerciseData:
        expr = self._parse_expression(parsed.expression)
        result = simplify(expr)
        return SolvedExerciseData(
            problem_type=parsed.problem_type,
            sympy_input=str(expr),
            final_result=str(result),
            steps=[
                f"Se identifica la expresion como \\({self._to_latex(expr)}\\).",
                "Se combinan terminos y operaciones equivalentes.",
                f"La forma simplificada es \\({self._to_latex(result)}\\).",
            ],
        )

    def _parse_expression(self, expression: str):
        return parse_expr(
            expression,
            local_dict=self.local_dict.copy(),
            transformations=self._transformations,
            evaluate=True,
        )

    @staticmethod
    def _resolve_symbol(variable_hint: str | None, expressions: list) -> Symbol:
        if variable_hint:
            return Symbol(variable_hint)

        free_symbols = sorted(
            {symbol for expr in expressions for symbol in expr.free_symbols},
            key=lambda item: item.name,
        )
        if free_symbols:
            return free_symbols[0]
        return Symbol("x")

    @staticmethod
    def _to_latex(value) -> str:
        try:
            return latex(value)
        except Exception:
            return str(value).replace("**", "^")

    @classmethod
    def _to_latex_text(cls, value: str) -> str:
        if "=" in value:
            left, right = value.split("=", maxsplit=1)
            return f"{left.strip()} = {right.strip().replace('**', '^')}"
        return value.replace("**", "^")
