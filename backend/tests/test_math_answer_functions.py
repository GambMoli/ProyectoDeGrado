from sympy import Symbol, cos, exp, log, pi, sin, sqrt, tan
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.services.practice.math import answers_match, integral_answers_match

_transformations = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

_local_dict: dict = {name: Symbol(name) for name in "x y z t n a b c".split()}
_local_dict.update({"sin": sin, "cos": cos, "tan": tan, "ln": log, "log": log, "exp": exp, "sqrt": sqrt, "pi": pi})


def _parse(expr: str):
    return parse_expr(expr, local_dict=_local_dict.copy(), transformations=_transformations, evaluate=True)


class TestAnswersMatch:
    class TestNormal:
        def test_derivada_correcta_retorna_true(self) -> None:
            assert answers_match(
                expected_answer="2*x",
                student_answer="2*x",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_derivada_equivalente_simbolicamente_retorna_true(self) -> None:
            assert answers_match(
                expected_answer="2*x",
                student_answer="x + x",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_integral_con_constante_mayuscula_normalizada(self) -> None:
            assert answers_match(
                expected_answer="x**2/2 + C",
                student_answer="x**2/2 + c",
                problem_type="integral",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_ecuacion_con_x_igual_retorna_true(self) -> None:
            assert answers_match(
                expected_answer="x = 2",
                student_answer="2",
                problem_type="equation",
                local_dict=_local_dict,
                transformations=_transformations,
            )

    class TestLimite:
        def test_respuesta_diferente_retorna_false(self) -> None:
            assert not answers_match(
                expected_answer="2*x",
                student_answer="3*x",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_integral_diferente_en_constante_retorna_true(self) -> None:
            assert answers_match(
                expected_answer="x**2/2 + c",
                student_answer="x**2/2 + 5",
                problem_type="integral",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_expresiones_con_potencias_xor_equivalentes(self) -> None:
            assert answers_match(
                expected_answer="x**2",
                student_answer="x^2",
                problem_type="simplification",
                local_dict=_local_dict,
                transformations=_transformations,
            )

    class TestError:
        def test_student_answer_vacia_retorna_false(self) -> None:
            assert not answers_match(
                expected_answer="2*x",
                student_answer="",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_expresion_no_parseable_retorna_false(self) -> None:
            assert not answers_match(
                expected_answer="2*x",
                student_answer="no es math @@##",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )

        def test_expected_no_parseable_retorna_false(self) -> None:
            assert not answers_match(
                expected_answer="@@invalido",
                student_answer="2*x",
                problem_type="derivative",
                local_dict=_local_dict,
                transformations=_transformations,
            )


class TestIntegralAnswersMatch:
    class TestNormal:
        def test_antiderivadas_equivalentes_retornan_true(self) -> None:
            x = Symbol("x")
            expected = x**2 / 2
            student = x**2 / 2
            assert integral_answers_match(expected_expr=expected, student_expr=student)

        def test_antiderivadas_difieren_en_constante_retornan_true(self) -> None:
            x = Symbol("x")
            expected = x**2 / 2
            student = x**2 / 2 + 5
            assert integral_answers_match(expected_expr=expected, student_expr=student)

        def test_sin_x_antiderivada(self) -> None:
            x = Symbol("x")
            expected = -cos(x)
            student = -cos(x) + 3
            assert integral_answers_match(expected_expr=expected, student_expr=student)

    class TestLimite:
        def test_antiderivadas_completamente_distintas_retornan_false(self) -> None:
            x = Symbol("x")
            expected = x**2 / 2
            student = x**3 / 3
            assert not integral_answers_match(expected_expr=expected, student_expr=student)

        def test_con_multiples_variables_usa_primera_alfabeticamente(self) -> None:
            x, y = Symbol("x"), Symbol("y")
            expected = x**2 / 2 + y
            student = x**2 / 2 + y + 1
            assert integral_answers_match(expected_expr=expected, student_expr=student)

    class TestError:
        def test_constante_vs_funcion_retorna_false(self) -> None:
            x = Symbol("x")
            expected = x**2
            student = Symbol("c")
            assert not integral_answers_match(expected_expr=expected, student_expr=student)
