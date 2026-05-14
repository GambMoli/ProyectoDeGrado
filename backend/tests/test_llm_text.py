from app.utils.llm_text import normalize_llm_math_text


class TestNormalizeLlmMathText:
    class TestNormal:
        def test_preserva_delimitadores_latex_inline(self) -> None:
            result = normalize_llm_math_text(r"La derivada de \(x^2\) es \(2x\).")
            assert r"\(" in result
            assert r"\)" in result

        def test_elimina_left_y_right(self) -> None:
            result = normalize_llm_math_text(r"\left( x + 1 \right)")
            assert r"\left" not in result
            assert r"\right" not in result

        def test_elimina_negritas_markdown(self) -> None:
            result = normalize_llm_math_text("El resultado es **2x**.")
            assert "**" not in result
            assert "2x" in result

    class TestLimite:
        def test_preserva_frac_latex(self) -> None:
            result = normalize_llm_math_text(r"\frac{x^2}{2}")
            assert r"\frac" in result

        def test_reduce_multiples_saltos_de_linea(self) -> None:
            result = normalize_llm_math_text("linea1\n\n\n\nlinea2")
            assert "\n\n\n" not in result

        def test_string_solo_espacios_retorna_vacio(self) -> None:
            assert normalize_llm_math_text("   ") == ""

    class TestError:
        def test_string_vacio_retorna_vacio(self) -> None:
            assert normalize_llm_math_text("") == ""

        def test_texto_sin_latex_pasa_sin_cambios(self) -> None:
            result = normalize_llm_math_text("texto plano sin math")
            assert result == "texto plano sin math"
