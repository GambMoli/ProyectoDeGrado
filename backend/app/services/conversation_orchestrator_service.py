from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from app.schemas.enums import ChatMode
from app.services.math_parser_service import MathParserService, ParsedExercise
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.utils.llm_text import normalize_llm_math_text

if TYPE_CHECKING:
    from app.core.config import Settings


OrchestratorMode = Literal["direct", "tool"]
OrchestratorAction = Literal[
    "answer_theory",
    "solve_exercise",
    "generate_practice",
    "explain_practice_context",
    "grade_practice",
    "ask_clarification",
]
DetailLevel = Literal["auto", "brief", "detailed"]


@dataclass(slots=True)
class OrchestratedTurn:
    mode: OrchestratorMode
    actions: list[OrchestratorAction]
    reason: str
    topic: str | None = None
    detail_level: DetailLevel = "auto"
    reply: str | None = None
    confidence: float = 0.0


class ConversationOrchestratorService:
    _allowed_actions: tuple[OrchestratorAction, ...] = (
        "answer_theory",
        "solve_exercise",
        "generate_practice",
        "explain_practice_context",
        "grade_practice",
        "ask_clarification",
    )

    def __init__(
        self,
        settings: Settings,
        ollama_client: OllamaClient | None = None,
        parser_service: MathParserService | None = None,
    ) -> None:
        self.settings = settings
        self.ollama_client = ollama_client
        self.parser_service = parser_service

    def orchestrate(
        self,
        *,
        message: str,
        requested_mode: ChatMode,
        conversation_context: list[str],
        agent_state: dict | None,
    ) -> OrchestratedTurn | None:
        if requested_mode != ChatMode.AUTO or not self.ollama_client:
            return None

        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        current_candidate = self._parse_candidate(message)
        active_candidate = self._practice_candidate(agent_state or {}, "pending_practice")
        recent_candidate = self._practice_candidate(agent_state or {}, "last_practice_context")
        explicit_new_exercise = self._is_explicit_new_exercise(
            current_candidate=current_candidate,
            active_candidate=active_candidate,
            recent_candidate=recent_candidate,
        )
        prompt = f"""
Eres el tutor principal de una conversacion de calculo y metodos numericos.

Tu trabajo es decidir libremente si:
1. respondes directamente al estudiante con una sola respuesta natural, o
2. pides una herramienta del sistema para apoyarte.

No eres un clasificador de palabras. Debes usar semantica, continuidad conversacional y estado pedagogico.

Mensaje actual del estudiante:
{message}

Contexto reciente:
{history}

Estado pedagogico:
{json.dumps(agent_state or {}, ensure_ascii=False)}

Analisis estructurado del mensaje actual:
{self._candidate_summary(current_candidate)}

Practica activa comparable:
{self._candidate_summary(active_candidate)}

Practica reciente comparable:
{self._candidate_summary(recent_candidate)}

Herramientas disponibles:
- answer_theory: para explicar un tema usando corpus/recuperacion.
- solve_exercise: para resolver un problema matematico nuevo.
- generate_practice: para proponer un ejercicio nuevo.
- explain_practice_context: para desarrollar un ejercicio activo o reciente.
- grade_practice: para calificar una respuesta del estudiante.
- ask_clarification: solo si de verdad no puedes inferir el objetivo.

Reglas de criterio:
- Si puedes responder directamente usando el contexto ya disponible, hazlo.
- Si el estudiante continua un ejercicio activo o reciente, puedes responder directamente o usar explain_practice_context si eso ayuda mas.
- Si pide un ejercicio nuevo, usa generate_practice.
- Si trae un problema nuevo concreto para resolver, usa solve_exercise.
- Si el analisis estructurado del mensaje actual muestra un ejercicio nuevo explicito distinto del que esta en contexto, prioriza solve_exercise y no sigas respondiendo sobre el ejercicio anterior.
- Si esta entregando su intento de respuesta al ejercicio activo, usa grade_practice.
- Si pide teoria apoyada en el curso, usa answer_theory.
- Usa ask_clarification solo cuando sea realmente necesario.

Devuelve solo JSON valido con una de estas formas:

Respuesta directa:
{{
  "mode":"direct",
  "reply":"...",
  "reason":"...",
  "topic":"integral",
  "detail_level":"detailed",
  "confidence":0.90
}}

Uso de herramienta:
{{
  "mode":"tool",
  "actions":["explain_practice_context"],
  "reason":"...",
  "topic":"integral",
  "detail_level":"detailed",
  "confidence":0.88
}}
""".strip()

        try:
            raw = self.ollama_client.generate(
                system_prompt="Eres un tutor-orquestador interno. Devuelves solo JSON valido.",
                prompt=prompt,
                temperature=0.15,
            )
            payload = self._extract_json(raw)
        except (OllamaClientError, ValueError, json.JSONDecodeError):
            return None

        mode = payload.get("mode")
        if mode not in {"direct", "tool"}:
            return None

        confidence = self._normalize_confidence(payload.get("confidence"))
        if confidence < 0.55:
            return None

        detail_level = self._normalize_detail_level(payload.get("detail_level"))
        topic = str(payload.get("topic")) if payload.get("topic") is not None else None
        reason = str(payload.get("reason") or "llm_orchestrator")

        if explicit_new_exercise:
            return OrchestratedTurn(
                mode="tool",
                actions=["solve_exercise"],
                reason=f"explicit_new_exercise_{reason}",
                topic=topic or (current_candidate.problem_type.value if current_candidate else None),
                detail_level="detailed",
                confidence=max(confidence, 0.9),
            )

        if mode == "direct":
            reply = str(payload.get("reply") or "").strip()
            if not reply:
                return None
            return OrchestratedTurn(
                mode="direct",
                actions=[],
                reason=reason,
                topic=topic,
                detail_level=detail_level,
                reply=normalize_llm_math_text(reply),
                confidence=confidence,
            )

        actions = self._normalize_actions(payload.get("actions"))
        if not actions:
            return None

        return OrchestratedTurn(
            mode="tool",
            actions=actions,
            reason=reason,
            topic=topic,
            detail_level=detail_level,
            confidence=confidence,
        )

    @staticmethod
    def _extract_json(raw: str) -> dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in orchestrator response.")
        return json.loads(match.group(0))

    def _normalize_actions(self, raw_actions: object) -> list[OrchestratorAction]:
        if not isinstance(raw_actions, list):
            return []

        normalized: list[OrchestratorAction] = []
        for raw_action in raw_actions:
            if raw_action not in self._allowed_actions:
                continue
            action = raw_action
            if action not in normalized:
                normalized.append(action)
        return normalized

    @staticmethod
    def _normalize_detail_level(raw_value: object) -> DetailLevel:
        if raw_value in {"brief", "detailed", "auto"}:
            return raw_value
        return "auto"

    @staticmethod
    def _normalize_confidence(raw_value: object) -> float:
        try:
            confidence = float(raw_value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, confidence))

    def _parse_candidate(self, raw_text: str) -> ParsedExercise | None:
        if not self.parser_service:
            return None
        try:
            return self.parser_service.parse(raw_text)
        except Exception:
            return None

    def _practice_candidate(self, agent_state: dict, key: str) -> ParsedExercise | None:
        context = dict(agent_state or {}).get(key) or {}
        raw_input = str(context.get("raw_input") or "").strip()
        if not raw_input:
            return None
        return self._parse_candidate(raw_input)

    @staticmethod
    def _candidate_summary(candidate: ParsedExercise | None) -> str:
        if not candidate:
            return "No se detecto ejercicio estructurado."
        return json.dumps(
            {
                "problem_type": candidate.problem_type.value,
                "expression": candidate.expression,
                "variable": candidate.variable,
                "limit_point": candidate.limit_point,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _signature(candidate: ParsedExercise | None) -> tuple[str, str, str, str] | None:
        if not candidate:
            return None
        return (
            candidate.problem_type.value,
            candidate.expression.strip(),
            str(candidate.variable or "").strip(),
            str(candidate.limit_point or "").strip(),
        )

    def _is_explicit_new_exercise(
        self,
        *,
        current_candidate: ParsedExercise | None,
        active_candidate: ParsedExercise | None,
        recent_candidate: ParsedExercise | None,
    ) -> bool:
        current_signature = self._signature(current_candidate)
        if not current_signature:
            return False

        active_signature = self._signature(active_candidate)
        recent_signature = self._signature(recent_candidate)
        if active_signature and current_signature == active_signature:
            return False
        if recent_signature and current_signature == recent_signature:
            return False
        return True
