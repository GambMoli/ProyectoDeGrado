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
    "answer_theory_with_practice",
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
        "otro ejercicio",
        "nuevo ejercicio",
    )
    _new_task_patterns = (
        "resuelve",
        "deriva",
        "derivada de",
        "integral de",
        "lim ",
        "limite",
        "explicame",
        "que es",
        "que sabes",
        "como funciona",
        "quiero cambiar de tema",
        "cambiando de tema",
    )
    _practice_correction_patterns = (
        "no de",
        "no era",
        "eso es de",
        "eso era de",
        "te pedi",
        "repito",
    )
    _theory_patterns = (
        "que sabes",
        "explicame",
        "que es",
        "como funciona",
        "tema",
        "curso",
        "unidad",
    )
    _explicit_answer_markers = (
        "resultado",
        "respuesta",
        "creo que",
        "me dio",
        "seria",
        "mi resultado",
        "mi respuesta",
    )
    _topic_aliases = (
        ("serie_de_taylor", ("serie de taylor", "taylor")),
        ("newton_raphson", ("newton raphson", "newton-raphson")),
        ("regula_falsi", ("regula falsi", "falsa posicion")),
        ("metodo_de_la_secante", ("metodo de la secante", "secante")),
        ("punto_fijo", ("punto fijo",)),
        ("biseccion", ("biseccion",)),
        ("lagrange", ("lagrange",)),
        ("interpolacion_newton", ("interpolacion de newton",)),
        ("simpson_1_3", ("simpson 1/3", "simpson 1 3", "simpson un tercio")),
        ("trapecios", ("trapecio", "trapecios")),
        ("derivative", ("derivad",)),
        ("integral", ("integral",)),
        ("limit", ("limite", "lim ")),
        ("equation", ("ecuacion",)),
    )
    _token_pattern = re.compile(r"[a-z0-9]+")

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
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        state = agent_state or {}
        decision = self._decide_with_ollama(
            message=message,
            conversation_context=conversation_context,
            agent_state=state,
        )
        if not decision:
            decision = self._decide_with_rules(
                message=message,
                conversation_context=conversation_context,
                agent_state=state,
            )
        return self._apply_guardrails(
            decision=decision,
            message=message,
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
- answer_theory_with_practice
- solve_exercise
- generate_practice
- grade_practice
- ask_clarification

Reglas:
- Una practica pendiente no bloquea la conversacion. Si el estudiante cambia de tema o abre una tarea nueva, sigue la nueva intencion.
- Usa grade_practice solo cuando el mensaje parezca realmente una respuesta al ejercicio pendiente, no por ser simplemente texto matematico.
- Usa answer_theory_with_practice si el estudiante pide explicacion o teoria y, al mismo tiempo, quiere que le propongas un ejercicio.
- Usa generate_practice si el estudiante pide que le propongan o le den un ejercicio.
- Si corrige el tema de una practica pendiente, usa generate_practice con el tema corregido.
- Usa solve_exercise si esta pidiendo resolver un ejercicio concreto o comparte una nueva expresion para trabajarla.
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
                "answer_theory_with_practice",
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

    def _decide_with_rules(
        self,
        *,
        message: str,
        conversation_context: list[str],
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
                reason="rule_practice_topic_correction",
                topic=detected_topic,
            )

        if self._looks_like_mixed_theory_practice_request(normalized):
            return TutorAgentDecision(
                action="answer_theory_with_practice",
                reason="rule_mixed_theory_practice",
                topic=detected_topic,
            )

        if any(pattern in normalized for pattern in self._practice_patterns):
            return TutorAgentDecision(
                action="generate_practice",
                reason="rule_practice_request",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return TutorAgentDecision(
                action="grade_practice",
                reason="rule_pending_practice_answer",
                topic=str(pending_practice.get("topic") or ""),
            )

        if self._looks_like_theory_query(normalized):
            return TutorAgentDecision(
                action="answer_theory",
                reason="rule_theory_query",
                topic=detected_topic,
            )

        try:
            self.parser_service.parse(message)
            return TutorAgentDecision(
                action="solve_exercise",
                reason="rule_parser_detected_exercise",
                topic=detected_topic,
            )
        except Exception:
            pass

        return TutorAgentDecision(
            action="ask_clarification",
            reason="rule_fallback_clarification",
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

        if self._looks_like_mixed_theory_practice_request(normalized):
            return TutorAgentDecision(
                action="answer_theory_with_practice",
                reason="guardrail_mixed_theory_practice",
                topic=detected_topic,
            )

        if any(pattern in normalized for pattern in self._practice_patterns):
            return TutorAgentDecision(
                action="generate_practice",
                reason="guardrail_practice_request",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_theory_query(normalized):
            return TutorAgentDecision(
                action="answer_theory",
                reason="guardrail_context_switch_theory",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_new_math_task(
            message=message,
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return TutorAgentDecision(
                action="solve_exercise",
                reason="guardrail_context_switch_new_math",
                topic=detected_topic,
            )

        if pending_practice and self._looks_like_practice_attempt(
            normalized_message=normalized,
            pending_practice=pending_practice,
        ):
            return TutorAgentDecision(
                action="grade_practice",
                reason="guardrail_pending_practice",
                topic=str(pending_practice.get("topic") or ""),
            )

        if decision.action == "grade_practice" and pending_practice:
            rerouted = self._reroute_if_pending_practice_does_not_fit(
                message=message,
                normalized_message=normalized,
                pending_practice=pending_practice,
                detected_topic=detected_topic,
            )
            if rerouted:
                return rerouted

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

    def _reroute_if_pending_practice_does_not_fit(
        self,
        *,
        message: str,
        normalized_message: str,
        pending_practice: dict,
        detected_topic: str | None,
    ) -> TutorAgentDecision | None:
        if self._looks_like_practice_attempt(
            normalized_message=normalized_message,
            pending_practice=pending_practice,
        ):
            return None

        if self._looks_like_mixed_theory_practice_request(normalized_message):
            return TutorAgentDecision(
                action="answer_theory_with_practice",
                reason="guardrail_reroute_theory_with_practice",
                topic=detected_topic,
            )

        if self._looks_like_theory_query(normalized_message):
            return TutorAgentDecision(
                action="answer_theory",
                reason="guardrail_reroute_theory",
                topic=detected_topic,
            )

        if self._looks_like_new_math_task(
            message=message,
            normalized_message=normalized_message,
            pending_practice=pending_practice,
        ):
            return TutorAgentDecision(
                action="solve_exercise",
                reason="guardrail_reroute_new_math",
                topic=detected_topic,
            )

        return None

    @staticmethod
    def _extract_json(raw: str) -> dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in agent response.")
        return json.loads(match.group(0))

    @classmethod
    def _looks_like_practice_attempt(
        cls,
        *,
        normalized_message: str,
        pending_practice: dict,
    ) -> bool:
        if cls._looks_like_theory_query(normalized_message):
            return False

        if any(pattern in normalized_message for pattern in cls._practice_patterns):
            return False

        if any(pattern in normalized_message for pattern in cls._new_task_patterns):
            return False

        if any(marker in normalized_message for marker in cls._explicit_answer_markers):
            return True

        expected_answer = str(pending_practice.get("expected_answer") or "")
        student_tokens = cls._math_tokens(normalized_message)
        expected_tokens = cls._math_tokens(expected_answer)
        if not student_tokens or not expected_tokens:
            return False

        overlap = len(student_tokens.intersection(expected_tokens))
        student_overlap = overlap / len(student_tokens)
        expected_overlap = overlap / len(expected_tokens)
        return student_overlap >= 0.75 and expected_overlap >= 0.5

    def _looks_like_new_math_task(
        self,
        *,
        message: str,
        normalized_message: str,
        pending_practice: dict,
    ) -> bool:
        if self._looks_like_practice_attempt(
            normalized_message=normalized_message,
            pending_practice=pending_practice,
        ):
            return False

        if self._looks_like_theory_query(normalized_message):
            return False

        try:
            self.parser_service.parse(message)
            return True
        except Exception:
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

    @classmethod
    def _looks_like_mixed_theory_practice_request(cls, normalized_message: str) -> bool:
        return cls._looks_like_theory_query(normalized_message) and any(
            pattern in normalized_message for pattern in cls._practice_patterns
        )

    @classmethod
    def _math_tokens(cls, value: str) -> set[str]:
        normalized = normalize_search_text(value)
        return {
            token
            for token in cls._token_pattern.findall(normalized)
            if token not in {"el", "la", "de", "es", "mi", "resultado", "respuesta"}
        }
