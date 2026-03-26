from app.utils.expression_normalizer import looks_like_structured_math


def test_structured_math_detects_valid_expression() -> None:
    assert looks_like_structured_math("2*x + 3 = 7")


def test_structured_math_rejects_ocr_garbage() -> None:
    assert not looks_like_structured_math("cv 2826 See Oe ee acy SS SU")
