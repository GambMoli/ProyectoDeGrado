from __future__ import annotations

import re


def normalize_llm_math_text(text: str) -> str:
    normalized = text.strip()
    normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", normalized)
    normalized = re.sub(r"^\* ", "- ", normalized, flags=re.MULTILINE)
    normalized = normalized.replace("\\left", "")
    normalized = normalized.replace("\\right", "")
    normalized = normalized.replace("```latex", "```")
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()
