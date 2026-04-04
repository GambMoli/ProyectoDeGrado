from app.utils.expression_normalizer import looks_like_structured_math, normalize_text


def test_structured_math_detects_valid_expression() -> None:
    assert looks_like_structured_math("2*x + 3 = 7")


def test_structured_math_rejects_ocr_garbage() -> None:
    assert not looks_like_structured_math("cv 2826 See Oe ee acy SS SU")


def test_normalize_text_supports_unicode_and_latex_math() -> None:
    normalized = normalize_text(r"\int 3x^2 e^x \, dx")

    assert "integral" in normalized
    assert "dx" in normalized


def test_structured_math_detects_unicode_integral() -> None:
    assert looks_like_structured_math("∫ 3x^2 e^x dx")
