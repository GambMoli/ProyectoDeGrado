from __future__ import annotations

from app.services.practice.math import extract_student_answer


class TestExtractStudentAnswer:
    class TestNormal:
        def test_strips_el_resultado_es(self) -> None:
            assert extract_student_answer("el resultado es 2*x") == "2*x"

        def test_strips_mi_respuesta_es(self) -> None:
            assert extract_student_answer("mi respuesta es x^2 + 1") == "x^2 + 1"

        def test_strips_resultado_colon(self) -> None:
            assert extract_student_answer("resultado: 3*x") == "3*x"

        def test_strips_respuesta_colon(self) -> None:
            assert extract_student_answer("respuesta: x/2") == "x/2"

        def test_strips_creo_que_es(self) -> None:
            assert extract_student_answer("creo que es 5") == "5"

        def test_retorna_expresion_sin_prefijo_sin_cambios(self) -> None:
            assert extract_student_answer("2*x + 1") == "2*x + 1"

    class TestLimite:
        def test_extrae_lado_derecho_con_keyword_integral(self) -> None:
            assert "x^2/2" in extract_student_answer("la integral = x^2/2")

        def test_elimina_espacios_extra(self) -> None:
            assert extract_student_answer("  el resultado es   3*x^2  ") == "3*x^2"

        def test_strips_es_prefijo_simple(self) -> None:
            assert extract_student_answer("es 2*x + 3") == "2*x + 3"

        def test_prefijo_en_mayusculas(self) -> None:
            assert extract_student_answer("El resultado es x + 1") == "x + 1"

    class TestError:
        def test_maneja_string_vacio(self) -> None:
            assert extract_student_answer("") == ""

        def test_maneja_solo_espacios(self) -> None:
            assert extract_student_answer("   ") == ""
