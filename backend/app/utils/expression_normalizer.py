from __future__ import annotations

import re

_REPLACEMENTS = {
    "−": "-",
    "–": "-",
    "—": "-",
    "×": "*",
    "·": "*",
    "÷": "/",
    "π": "pi",
    "√": "sqrt",
    "∫": "integral ",
    "∞": "oo",
    "→": "->",
    "²": "^2",
    "³": "^3",
    "⁴": "^4",
    "⁵": "^5",
    "⁶": "^6",
    "⁷": "^7",
    "⁸": "^8",
    "⁹": "^9",
    "sen": "sin",
}

_LATEX_REPLACEMENTS = (
    (r"\frac{d}{dx}", "d/dx"),
    (r"\frac{d}{dy}", "d/dy"),
    (r"\frac{d}{dt}", "d/dt"),
    (r"\cdot", "*"),
    (r"\times", "*"),
    (r"\div", "/"),
    (r"\pi", "pi"),
    (r"\sin", "sin"),
    (r"\cos", "cos"),
    (r"\tan", "tan"),
    (r"\ln", "ln"),
    (r"\log", "log"),
    (r"\sqrt", "sqrt"),
    (r"\to", "->"),
    (r"\infty", "oo"),
    (r"\int", "integral "),
    (r"\,", " "),
    (r"\;", " "),
    (r"\:", " "),
    (r"\!", ""),
    (r"\left", ""),
    (r"\right", ""),
)


def normalize_text(raw_text: str) -> str:
    text = raw_text.strip()
    for source, target in _REPLACEMENTS.items():
        text = text.replace(source, target)
    text = _normalize_latex(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_latex(text: str) -> str:
    normalized = text
    normalized = normalized.replace(r"\(", " ").replace(r"\)", " ")
    normalized = normalized.replace(r"\[", " ").replace(r"\]", " ")
    normalized = normalized.replace("$$", " ").replace("$", " ")

    for source, target in _LATEX_REPLACEMENTS:
        normalized = normalized.replace(source, target)

    normalized = _normalize_latex_fractions(normalized)
    normalized = re.sub(r"sqrt\s*\{([^{}]+)\}", r"sqrt(\1)", normalized)
    normalized = re.sub(r"e\s*\^\s*\{([^{}]+)\}", r"exp(\1)", normalized)
    normalized = normalized.replace("{", " ").replace("}", " ")
    return normalized


def _normalize_latex_fractions(text: str) -> str:
    pattern = re.compile(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}")
    normalized = text
    while True:
        updated = pattern.sub(r"(\1)/(\2)", normalized)
        if updated == normalized:
            break
        normalized = updated
    return normalized


def extract_candidate_segment(text: str) -> str:
    if ":" in text:
        segments = [segment.strip() for segment in text.split(":") if segment.strip()]
        for segment in reversed(segments):
            if looks_like_structured_math(segment):
                return segment

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines):
        if looks_like_structured_math(line):
            return line
    return text.strip()


def looks_like_math(text: str) -> bool:
    lowered = text.lower()
    if re.search(r"[=+\-*/^()]", text):
        return True
    if re.search(r"\b(?:sin|cos|tan|log|ln|sqrt|integral|derivada|limit|lim|ecuacion|ecuación)\b", lowered):
        return True
    if re.search(r"\d", text) and re.search(r"[a-zA-Z]", text):
        return True
    if re.search(r"\bd[a-zA-Z]\b", text):
        return True
    return False


def looks_like_structured_math(text: str) -> bool:
    normalized = normalize_text(text)
    lowered = normalized.lower()
    if re.search(r"[=+\-*/^()]", normalized):
        return True
    if re.search(
        r"\b(?:sin|cos|tan|log|ln|sqrt|integral|derivada|limit|lim|ecuacion|ecuación)\b",
        lowered,
    ):
        return True
    if re.search(r"\b[xyztn]\s*\^\s*\d+\b", lowered):
        return True
    if re.search(r"\b\d+\s*[xyztn]\b", lowered):
        return True
    if re.search(r"\bd[xyztn]\b", lowered):
        return True
    if re.search(r"\b[xyztn]\s*->\s*[-+]?\d", lowered):
        return True
    return False
