from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services.ollama_client import OllamaClient, OllamaClientError

if TYPE_CHECKING:
    from app.core.config import Settings


@dataclass(slots=True)
class ComposedResponse:
    text: str
    source: str


class ResponseComposerService:
    def __init__(self, settings: Settings, ollama_client: OllamaClient | None = None) -> None:
        self.settings = settings
        self.ollama_client = ollama_client
        self.system_prompt = (
            "Eres un tutor de calculo y metodos numericos. "
            "Redactas una sola respuesta natural, clara y humana a partir de resultados internos del sistema. "
            "No inventas expresiones matematicas nuevas ni alteras los ejercicios dados. "
            "No uses encabezados ni texto de plantilla."
        )

    def compose_guidance(
        self,
        *,
        user_message: str,
        conversation_context: list[str],
        theory_text: str | None = None,
        exercise_text: str | None = None,
        hint: str | None = None,
        detail_level: str = "auto",
    ) -> ComposedResponse:
        if theory_text and exercise_text:
            fallback = self._fallback_theory_with_practice(
                theory_text=theory_text,
                exercise_text=exercise_text,
                hint=hint or "",
            )
        elif exercise_text:
            fallback = self._fallback_practice(
                exercise_text=exercise_text,
                hint=hint or "",
            )
        elif theory_text:
            fallback = theory_text.strip()
        else:
            fallback = "Dime con mas precision que tema o ejercicio quieres trabajar."

        if not self.ollama_client or not exercise_text:
            return ComposedResponse(text=fallback, source="fallback")

        history_block = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        prompt = f"""
Mensaje del estudiante:
{user_message}

Contexto reciente:
{history_block}

Nivel de detalle:
{detail_level}

Explicacion base:
{theory_text or "No aplica"}

Ejercicio que debes incluir literalmente, sin cambiarlo:
{exercise_text}

Pista disponible:
{hint or "No aplica"}

Escribe una sola respuesta final.
- Si hay explicacion base, usala como sustancia principal, pero integrala con naturalidad.
- Presenta el ejercicio como continuidad organica de la conversacion, no como una segunda respuesta separada.
- Debes incluir literalmente el ejercicio dado.
- Si mencionas la pista, hazlo de forma natural.
- No uses frases como "Claro. Te propongo este ejercicio:" ni encabezados.
- No cierres con una pregunta obligatoria.
""".strip()

        try:
            text = self.ollama_client.generate(
                system_prompt=self.system_prompt,
                prompt=prompt,
            )
            normalized = self._normalize_text(text)
            if exercise_text not in normalized:
                return ComposedResponse(text=fallback, source="fallback_exact_exercise")
            return ComposedResponse(text=normalized, source="ollama_composer")
        except OllamaClientError:
            return ComposedResponse(text=fallback, source="fallback")

    @staticmethod
    def _fallback_practice(*, exercise_text: str, hint: str) -> str:
        return (
            f"Vamos con un ejercicio para practicar. {exercise_text} "
            "Intentalo por tu cuenta primero. "
            f"Si te trabas, apoyate en esta pista: {hint}"
        ).strip()

    @staticmethod
    def _fallback_theory_with_practice(*, theory_text: str, exercise_text: str, hint: str) -> str:
        return (
            f"{theory_text.strip()} Para aterrizar esa idea, intenta este ejercicio: "
            f"{exercise_text} No te doy la solucion completa todavia. "
            f"Si te atoras, puedes guiarte con esta pista: {hint}"
        ).strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        normalized = re.sub(r"^\* ", "- ", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()
