from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.enums import ChatMode
from app.services.knowledge_base_service import KnowledgeBaseService, normalize_search_text


@dataclass(slots=True)
class ChatIntent:
    mode: ChatMode
    reason: str


class IntentRouterService:
    _theory_patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in [
            r"\bexplica(?:me)?\b",
            r"\bque es\b",
            r"\bqué es\b",
            r"\bdefine\b",
            r"\bdefinicion\b",
            r"\bdefinición\b",
            r"\btema\b",
            r"\bconcepto\b",
            r"\bpara que sirve\b",
            r"\bpara qué sirve\b",
            r"\bcuando se usa\b",
            r"\bcuándo se usa\b",
            r"\bdiferencia\b",
            r"\bresumen\b",
            r"\brepaso\b",
        ]
    ]
    _exercise_patterns = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in [
            r"\bresuelve\b",
            r"\bcalcula\b",
            r"\bhalla\b",
            r"\bencuentra\b",
            r"\bderiva\b",
            r"\bintegra\b",
            r"\bsimplifica\b",
            r"\blim\b",
            r"\becuacion\b",
            r"\becuación\b",
            r"\bpaso a paso esta integral\b",
            r"\bcomo resuelvo\b",
            r"\bcómo resuelvo\b",
        ]
    ]

    def __init__(self, knowledge_base_service: KnowledgeBaseService) -> None:
        self.knowledge_base_service = knowledge_base_service

    def detect(self, message: str, *, requested_mode: ChatMode) -> ChatIntent:
        if requested_mode != ChatMode.AUTO:
            return ChatIntent(mode=requested_mode, reason="requested_mode")

        normalized = normalize_search_text(message)
        if self._looks_like_exercise(normalized):
            return ChatIntent(mode=ChatMode.EXERCISE, reason="exercise_heuristic")

        if self._looks_like_theory(normalized) and self.knowledge_base_service.has_relevant_context(message):
            return ChatIntent(mode=ChatMode.THEORY, reason="theory_heuristic")

        if self.knowledge_base_service.has_relevant_context(message):
            return ChatIntent(mode=ChatMode.THEORY, reason="knowledge_match")

        return ChatIntent(mode=ChatMode.THEORY, reason="default_math_chat")

    def _looks_like_theory(self, normalized_message: str) -> bool:
        return any(pattern.search(normalized_message) for pattern in self._theory_patterns)

    def _looks_like_exercise(self, normalized_message: str) -> bool:
        if any(pattern.search(normalized_message) for pattern in self._exercise_patterns):
            return True
        if re.search(r"[=+\-*/^()]", normalized_message) and re.search(r"\d|x|y", normalized_message):
            return True
        if re.search(r"\bd\/d[a-z]\b", normalized_message):
            return True
        return False
