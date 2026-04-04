from app.utils.llm_text import normalize_llm_math_text


def test_normalize_llm_math_text_preserves_basic_latex_delimiters() -> None:
    text = r"La antiderivada de \(2x+3\) es \(\frac{x^2}{1} + 3x + C\)."

    normalized = normalize_llm_math_text(text)

    assert r"\(" in normalized
    assert r"\frac" in normalized
    assert r"\left" not in normalized
