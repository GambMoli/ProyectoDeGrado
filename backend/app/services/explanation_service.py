from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.core.config import Settings
from app.services.math_parser_service import ParsedExercise
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.services.sympy_solver_service import SolvedExerciseData

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GeneratedExplanation:
    text: str
    source: str


class ExplanationService:
    def __init__(self, settings: Settings, ollama_client: OllamaClient | None = None) -> None:
        self.settings = settings
        self.ollama_client = ollama_client
        self.system_prompt = (
            "Eres un tutor de calculo cercano y riguroso. "
            "Explicas paso a paso de forma clara, natural y pedagogica. "
            "No inventes operaciones ni resultados. Usa solo la informacion del sistema. "
            "Evita sonar como una plantilla y evita markdown innecesario. "
            "Si falta informacion, dilo explicitamente."
        )

    def generate(
        self,
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
    ) -> GeneratedExplanation:
        if self.ollama_client:
            try:
                prompt = self._build_prompt(parsed=parsed, solved=solved)
                text = self.ollama_client.generate(
                    system_prompt=self.system_prompt,
                    prompt=prompt,
                )
                return GeneratedExplanation(
                    text=self._normalize_llm_text(text),
                    source="ollama",
                )
            except OllamaClientError as exc:
                logger.warning("Falling back to template explanation: %s", exc)

        return GeneratedExplanation(
            text=self._build_template_explanation(parsed=parsed, solved=solved),
            source="template",
        )

    @staticmethod
    def _build_prompt(*, parsed: ParsedExercise, solved: SolvedExerciseData) -> str:
        steps = "\n".join(f"{index}. {step}" for index, step in enumerate(solved.steps, start=1))
        return f"""
Problema detectado: {parsed.problem_type.value}
Expresion extraida: {parsed.expression}
Variable: {parsed.variable or "no especificada"}
Punto del limite: {parsed.limit_point or "no aplica"}
Entrada interpretada por SymPy: {solved.sympy_input}
Resultado final: {solved.final_result}
Pasos base del sistema:
{steps}

Redacta una explicacion en espanol con estas reglas:
- Empieza explicando la idea principal con lenguaje natural.
- Desarrolla el procedimiento paso a paso, pero sin sonar robotico.
- Si ayuda, menciona por que se aplica esa regla o metodo.
- Cierra con el resultado final de manera breve.
- No uses encabezados rigidos ni asteriscos decorativos.
- No inventes nuevos calculos ni cambies el resultado.
""".strip()

    @staticmethod
    def _build_template_explanation(
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
    ) -> str:
        numbered_steps = "\n".join(
            f"{index}. {step}" for index, step in enumerate(solved.steps, start=1)
        )
        return (
            f"Se detecto un ejercicio de tipo {parsed.problem_type.value}.\n\n"
            "Paso a paso:\n"
            f"{numbered_steps}\n\n"
            f"Resultado final: {solved.final_result}"
        )

    @staticmethod
    def _normalize_llm_text(text: str) -> str:
        normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        normalized = re.sub(r"^\* ", "- ", normalized, flags=re.MULTILINE)
        return normalized.strip()
