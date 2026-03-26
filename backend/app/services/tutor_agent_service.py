from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from app.services.knowledge_base_service import KnowledgeBaseService, normalize_search_text
from app.services.math_parser_service import MathParserService
from app.services.ollama_client import OllamaClient, OllamaClientError

if TYPE_CHECKING:
    from app.core.config import Settings

AgentAction = Literal[
    "answer_theory",
    "solve_exercise",
    "generate_practice",
    "grade_practice",
    "ask_clarification",
]


@dataclass(slots=True)
class TutorAgentDecision:
    action: AgentAction
    reason: str
    topic: str | None = None


class TutorAgentService:
    _practice_patterns = (
        "proponme un ejercicio",
        "ponme un ejercicio",
        "dame un ejercicio",
        "quiero practicar",
        "quiero un ejercicio",
        "quiero intentarlo",
    )
    _practice_correction_patterns = (
        "no de",
        "no era",
        "eso es de",
        "eso era de",
        "te pedi",
        "te pedí",
        "repito",
    )
    _theory_patterns = (
        "que sabes",
        "qué sabes",
        "explicame",
        "explícame",
        "que es",
        "qué es",
        "como funciona",
        "cómo funciona",
        "tema",
        "curso",
        "unidad",
    )
    _topic_aliases = (
        ("serie_de_taylor", ("serie de taylor", "taylor")),
        ("newton_raphson", ("newton raphson", "newton-raphson")),
        ("regula_falsi", ("regula falsi", "falsa posicion", "falsa posición")),
        ("metodo_de_la_secante", ("metodo de la secante", "método de la secante", "secante")),
        ("punto_fijo", ("punto fijo",)),
        ("biseccion", ("biseccion", "bisección")),
        ("lagrange", ("lagrange",)),
        ("interpolacion_newton", ("interpolacion de newton", "interpolación de newton")),
        ("simpson_1_3", ("simpson 1/3", "simpson 1 3", "simpson un tercio")),
        ("trapecios", ("trapecio", "trapecios")),
        ("derivative", ("derivad",)),
        ("integral", ("integral",)),
        ("limit", ("limite", "límite", "lim ")),
        ("equation", ("ecuacion", "ecuación")),
    )

    def __init__(
        self,
        settings: Settings,
        knowledge_base_service: KnowledgeBaseService,
        parser_service: MathParserService,
        ollama_client: OllamaClient | None = None,
    ) -> None:
        self.settings = settings
        self.knowledge_base_service = knowledge_base_service
        self.parser_service = parser_service
        self.ollama_client = ollama_client

    def decide(
        self,
        *,
        message: str,
        conversation_context: list[str],
        agent_state: dict | None,
    ) -> TutorAgentDecision:
        state = agent_state or {}
        if self.ollama_client:
            decision = self._decide_with_ollama(
                message=message,
                conversation_context=conversation_context,
                agent_state=state,
            )
            if decision:
                return self._apply_guardrails(
                    decision=decision,
                    message=message,
                    agent_state=state,
                )

        return self._fallback_decision(
            message=message,
            conversation_context=conversation_context,
            agent_state=state,
        )

    def _decide_with_ollama(
        self,
        *,
        message: str,
        conversation_context: list[str],
        agent_state: dict,
    ) -> TutorAgentDecision | None:
        try:
            history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
            prompt = f"""
Eres el enrutador interno de un tutor matematico.

Mensaje actual:
{message}

Contexto reciente:
{history}

Estado del tutor:
{json.dumps(agent_state, ensure_ascii=False)}

Debes decidir una sola accion entre:
- answer_theory
- solve_exercise
- generate_practice
- grade_practice
- ask_clarification

Reglas:
- Usa grade_practice si hay un ejercicio pendiente y el estudiante esta intentando responderlo.
- Usa generate_practice si el estudiante pide que le propongan o le den un ejercicio.
- Si corrige el tema de una practica pendiente, usa generate_practice con el tema corregido.
- Usa solve_exercise si esta pidiendo resolver un ejercicio concreto.
- Usa answer_theory si esta preguntando teoria, contenido, definiciones o explicaciones.
- Usa ask_clarification si falta informacion y no conviene asumir.

Devuelve solo JSON valido con esta forma:
{{"action":"answer_theory","reason":"...","topic":"derivative"}}
""".strip()
            raw = self.ollama_client.generate(
                system_prompt="Eres un clasificador interno. Devuelves solo JSON valido.",
                prompt=prompt,
            )
            payload = self._extract_json(raw)
            action = payload.get("action")
            if action not in {
                "answer_theory",
                "solve_exercise",
                "generate_practice",
                "grade_practice",
                "ask_clarification",
            }:
                return None
            topic = payload.get("topic")
            if topic is not None:
                topic = str(topic)
            return TutorAgentDecision(
                action=action,
                reason=str(payload.get("reason", "ollama_router")),
                topic=topic,
            )
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

    def _fallback_decision(
        self,
        *,
        message: str,
        conversation_context: list[str],
        agent_state: dict,
    ) -> TutorAgentDecision:
        del conversation_context
        normalized = normalize_search_text(message)
        pending_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)

        if pending_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(pending_practice.get("topic") or ""),
            detected_topic=detected_topic,
        ):
            return TutorAgentDecision(
                action="generate_practice",
                reason="practice_topic_correction",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_practice_attempt(normalized):
            return TutorAgentDecision(
                action="grade_practice",
                reason="pending_practice_attempt",
                topic=str(pending_practice.get("topic") or ""),
            )

        if any(pattern in normalized for pattern in self._practice_patterns):
            return TutorAgentDecision(
                action="generate_practice",
                reason="practice_request",
                topic=detected_topic,
            )

        if self._looks_like_theory_query(normalized) and self.knowledge_base_service.has_relevant_context(message):
            return TutorAgentDecision(
                action="answer_theory",
                reason="theory_query",
                topic=detected_topic,
            )

        try:
            self.parser_service.parse(message)
            return TutorAgentDecision(
                action="solve_exercise",
                reason="parser_detected_exercise",
                topic=detected_topic,
            )
        except Exception:
            pass

        if self.knowledge_base_service.has_relevant_context(message):
            return TutorAgentDecision(
                action="answer_theory",
                reason="knowledge_match",
                topic=detected_topic,
            )

        if pending_practice:
            return TutorAgentDecision(
                action="grade_practice",
                reason="pending_practice_default",
                topic=str(pending_practice.get("topic") or ""),
            )

        return TutorAgentDecision(
            action="answer_theory",
            reason="default_theory_chat",
            topic=detected_topic,
        )

    def _apply_guardrails(
        self,
        *,
        decision: TutorAgentDecision,
        message: str,
        agent_state: dict,
    ) -> TutorAgentDecision:
        normalized = normalize_search_text(message)
        pending_practice = agent_state.get("pending_practice")
        detected_topic = self._detect_topic(normalized)

        if pending_practice and self._looks_like_practice_correction(
            normalized_message=normalized,
            pending_topic=str(pending_practice.get("topic") or ""),
            detected_topic=detected_topic,
        ):
            return TutorAgentDecision(
                action="generate_practice",
                reason="guardrail_practice_topic_correction",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_practice_attempt(normalized):
            return TutorAgentDecision(
                action="grade_practice",
                reason="guardrail_pending_practice",
                topic=str(pending_practice.get("topic") or ""),
            )

        if any(pattern in normalized for pattern in self._practice_patterns):
            return TutorAgentDecision(
                action="generate_practice",
                reason="guardrail_practice_request",
                topic=detected_topic,
            )

        if decision.action == "answer_theory" and not self._looks_like_theory_query(normalized):
            try:
                self.parser_service.parse(message)
                return TutorAgentDecision(
                    action="solve_exercise",
                    reason="guardrail_parser_detected_exercise",
                    topic=detected_topic,
                )
            except Exception:
                pass

        return decision

    @staticmethod
    def _extract_json(raw: str) -> dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in agent response.")
        return json.loads(match.group(0))

    @staticmethod
    def _looks_like_practice_attempt(normalized_message: str) -> bool:
        if any(
            token in normalized_message
            for token in ("resultado", "respuesta", "creo que", "me dio", "seria", "sería")
        ):
            return True
        if re.search(r"[=+\-*/^()]", normalized_message) and re.search(r"\d|x|y|z", normalized_message):
            return True
        return False

    @classmethod
    def _looks_like_practice_correction(
        cls,
        *,
        normalized_message: str,
        pending_topic: str,
        detected_topic: str | None,
    ) -> bool:
        if not detected_topic or detected_topic == pending_topic:
            return False
        return any(pattern in normalized_message for pattern in cls._practice_correction_patterns)

    def _detect_topic(self, normalized_message: str) -> str | None:
        for topic, aliases in self._topic_aliases:
            if any(alias in normalized_message for alias in aliases):
                return topic

        matches = self.knowledge_base_service.search(normalized_message, limit=1)
        if matches:
            return matches[0].document.topic

        if "practic" in normalized_message or "ejercicio" in normalized_message:
            return "practice"
        return None

    @classmethod
    def _looks_like_theory_query(cls, normalized_message: str) -> bool:
        return any(pattern in normalized_message for pattern in cls._theory_patterns)
