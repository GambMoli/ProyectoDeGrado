import pytest

from app.schemas.enums import ProblemType
from app.services.math_parser_service import MathParserError, MathParserService


class TestDetectProblemType:
    class TestNormal:
        def test_detecta_derivada_por_keyword(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("calcula la derivada de x^2", "x^2")
            assert result == ProblemType.DERIVATIVE

        def test_detecta_integral_por_keyword(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("calcula la integral de x^2", "x^2 dx")
            assert result == ProblemType.INTEGRAL

        def test_detecta_limite_por_keyword(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("calcula el limite de x cuando x->0", "x -> 0")
            assert result == ProblemType.LIMIT

        def test_detecta_ecuacion_por_signo_igual(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("resuelve la ecuacion", "x^2 = 4")
            assert result == ProblemType.EQUATION

        def test_detecta_simplificacion_por_keyword(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("simplifica la expresion", "x^2 + 2x + 1")
            assert result == ProblemType.SIMPLIFICATION

    class TestLimite:
        def test_detecta_derivada_por_notacion_d_dx(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("halla d/dx de x^3", "d/dx x^3")
            assert result == ProblemType.DERIVATIVE

        def test_detecta_integral_por_sufijo_dx(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("calcula", "x^2 dx")
            assert result == ProblemType.INTEGRAL

        def test_detecta_limite_por_flecha(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("halla el valor", "x -> 2")
            assert result == ProblemType.LIMIT

        def test_detecta_simplificacion_si_parece_math_estructurado(self) -> None:
            svc = MathParserService()
            result = svc._detect_problem_type("halla", "x^2 + 1")
            assert result == ProblemType.SIMPLIFICATION

    class TestError:
        def test_lanza_error_sin_math_claro(self) -> None:
            svc = MathParserService()
            with pytest.raises(MathParserError) as exc_info:
                svc._detect_problem_type("hola mundo texto normal", "abc def ghi")
            assert exc_info.value.code == "no_clear_exercise"

        def test_error_contiene_mensaje_usuario(self) -> None:
            svc = MathParserService()
            with pytest.raises(MathParserError) as exc_info:
                svc._detect_problem_type("nada matematico aqui", "palabras normales aqui")
            assert exc_info.value.user_message != ""


class TestCleanupExpression:
    class TestNormal:
        def test_elimina_instruccion_al_inicio(self) -> None:
            result = MathParserService._cleanup_expression("calcula x^2 + 1")
            assert "calcula" not in result.lower()
            assert "x^2" in result

        def test_elimina_signos_de_puntuacion_al_final(self) -> None:
            result = MathParserService._cleanup_expression("x^2 + 1.")
            assert not result.endswith(".")

        def test_normaliza_espacios(self) -> None:
            result = MathParserService._cleanup_expression("x^2   +   1")
            assert "  " not in result

    class TestLimite:
        def test_elimina_simbolo_integral_unicode(self) -> None:
            result = MathParserService._cleanup_expression("∫ x^2 dx")
            assert "∫" not in result

        def test_elimina_contexto_de_limite_al_final(self) -> None:
            result = MathParserService._cleanup_expression("x^2 cuando x tiende a 0")
            assert "tiende" not in result

        def test_string_solo_instruccion_retorna_vacio(self) -> None:
            result = MathParserService._cleanup_expression("calcula simplifica")
            assert result == "" or not any(w in result.lower() for w in ["calcula", "simplifica"])

    class TestError:
        def test_string_vacio_retorna_vacio(self) -> None:
            result = MathParserService._cleanup_expression("")
            assert result == ""

        def test_string_solo_espacios_retorna_vacio(self) -> None:
            result = MathParserService._cleanup_expression("   ")
            assert result == ""

        def test_puntuacion_sola_retorna_vacio(self) -> None:
            result = MathParserService._cleanup_expression("?!.,;:")
            assert result == ""
