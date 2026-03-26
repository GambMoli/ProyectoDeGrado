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
    "sen": "sin",
}


def normalize_text(raw_text: str) -> str:
    text = raw_text.strip()
    for source, target in _REPLACEMENTS.items():
        text = text.replace(source, target)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_candidate_segment(text: str) -> str:
    if ":" in text:
        segments = [segment.strip() for segment in text.split(":") if segment.strip()]
        for segment in reversed(segments):
            if looks_like_math(segment):
                return segment

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines):
        if looks_like_math(line):
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
