from app.utils.expression_normalizer import (
    extract_candidate_segment,
    looks_like_math,
    looks_like_structured_math,
    normalize_text,
)


class TestNormalizeText:
    class TestNormal:
        def test_convierte_simbolo_unicode_integral(self) -> None:
            assert "integral" in normalize_text("∫ x dx")

        def test_convierte_latex_frac_a_fraccion(self) -> None:
            assert "d/dx" in normalize_text(r"\frac{d}{dx}")

        def test_elimina_espacios_multiples(self) -> None:
            assert "  " not in normalize_text("x  +   y")

        def test_reemplaza_guion_unicode_por_menos(self) -> None:
            result = normalize_text("x − 1")
            assert "−" not in result and "-" in result

    class TestLimite:
        def test_texto_vacio_retorna_vacio(self) -> None:
            assert normalize_text("") == ""

        def test_elimina_espacios_al_inicio_y_final(self) -> None:
            result = normalize_text("   x^2   ")
            assert result == result.strip()

        def test_latex_con_multiples_comandos(self) -> None:
            result = normalize_text(r"\int 3x^2 e^x \, dx")
            assert "integral" in result and "dx" in result

    class TestError:
        def test_texto_sin_matematica_retorna_texto_limpio(self) -> None:
            assert normalize_text("hola mundo") == "hola mundo"


class TestLooksLikeMath:
    class TestNormal:
        def test_detecta_operador_aritmetico(self) -> None:
            assert looks_like_math("3 + x") is True

        def test_detecta_keyword_sin(self) -> None:
            assert looks_like_math("sin(x)") is True

        def test_detecta_combinacion_numero_letra(self) -> None:
            assert looks_like_math("3x") is True

        def test_detecta_notacion_derivada_dx(self) -> None:
            assert looks_like_math("dx") is True

        def test_detecta_ecuacion_con_igual(self) -> None:
            assert looks_like_math("x = 5") is True

    class TestLimite:
        def test_detecta_solo_parentesis(self) -> None:
            assert looks_like_math("()") is True

        def test_detecta_keyword_integral(self) -> None:
            assert looks_like_math("integral de x") is True

        def test_detecta_keyword_derivada(self) -> None:
            assert looks_like_math("derivada") is True

    class TestError:
        def test_rechaza_texto_en_prosa(self) -> None:
            assert looks_like_math("hola como estas hoy") is False

        def test_rechaza_string_vacio(self) -> None:
            assert looks_like_math("") is False

        def test_rechaza_letras_sin_contexto_matematico(self) -> None:
            assert looks_like_math("abc") is False


class TestLooksLikeStructuredMath:
    class TestNormal:
        def test_detecta_expresion_con_igual(self) -> None:
            assert looks_like_structured_math("2*x + 3 = 7")

        def test_detecta_integral_unicode(self) -> None:
            assert looks_like_structured_math("∫ 3x^2 e^x dx")

        def test_detecta_variable_con_potencia(self) -> None:
            assert looks_like_structured_math("x^2 + 1")

    class TestLimite:
        def test_detecta_notacion_limite(self) -> None:
            assert looks_like_structured_math("x -> 0")

        def test_detecta_coeficiente_numerico(self) -> None:
            assert looks_like_structured_math("3x")

    class TestError:
        def test_rechaza_texto_ocr_basura(self) -> None:
            assert not looks_like_structured_math("cv 2826 See Oe ee acy SS SU")

        def test_rechaza_string_vacio(self) -> None:
            assert not looks_like_structured_math("")


class TestExtractCandidateSegment:
    class TestNormal:
        def test_extrae_linea_matematica_de_texto_multilinea(self) -> None:
            result = extract_candidate_segment("Calcula la siguiente expresion\n2*x^2 + 3*x - 1")
            assert "2*x" in result

        def test_extrae_segmento_despues_de_dos_puntos(self) -> None:
            result = extract_candidate_segment("Ejercicio: integral de x^2 dx")
            assert "integral" in result or "x^2" in result

        def test_prefiere_ultima_linea_matematica(self) -> None:
            result = extract_candidate_segment("Texto\nPrimer paso: 2x\nResultado: x^2 + 1")
            assert "x^2" in result

    class TestLimite:
        def test_retorna_input_si_no_hay_matematica(self) -> None:
            text = "hola como estas hoy"
            assert extract_candidate_segment(text) == text.strip()

        def test_maneja_texto_con_solo_dos_puntos(self) -> None:
            result = extract_candidate_segment("Nota: sin contexto matematico")
            assert isinstance(result, str) and len(result) > 0

    class TestError:
        def test_maneja_string_vacio(self) -> None:
            assert extract_candidate_segment("") == ""
