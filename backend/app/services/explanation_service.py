from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.config import Settings
from app.services.math_parser_service import ParsedExercise
from app.services.ollama_client import OllamaClient, OllamaClientError
from app.services.sympy_solver_service import SolvedExerciseData
from app.utils.llm_text import normalize_llm_math_text

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
            "Trabajas sobre resultados ya verificados por el sistema. "
            "No inventes operaciones ni resultados. Usa solo la informacion del sistema. "
            "No contradigas el resultado final ni propongas metodos alternativos que lo cuestionen. "
            "Evita sonar como una plantilla y evita markdown innecesario. "
            "Si falta informacion, dilo explicitamente."
        )

    def generate(
        self,
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
        student_request: str | None = None,
    ) -> GeneratedExplanation:
        if not self._should_use_llm(student_request):
            return self.fallback(parsed=parsed, solved=solved)

        if not self.ollama_client:
            return self.fallback(parsed=parsed, solved=solved)

        prompt = self._build_prompt(
            parsed=parsed,
            solved=solved,
            student_request=student_request,
        )
        text = self.ollama_client.generate(
            system_prompt=self.system_prompt,
            prompt=prompt,
        )
        return GeneratedExplanation(
            text=self._normalize_llm_text(text),
            source="ollama",
        )

    def fallback(
        self,
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
    ) -> GeneratedExplanation:
        text = self._build_structured_fallback(parsed=parsed, solved=solved)
        return GeneratedExplanation(
            text=self._normalize_llm_text(text),
            source="fallback",
        )

    @classmethod
    def _build_structured_fallback(
        cls,
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
    ) -> str:
        expression = cls._math_inline(parsed.expression)
        result = cls._math_inline(solved.final_result)

        if parsed.problem_type.value == "limit":
            target = f"{cls._math_inline(parsed.variable or 'x')} \\to {cls._plain_to_latex(parsed.limit_point or '0')}"
            return (
                f"Queremos calcular el limite de {expression} cuando \\({target}\\). "
                f"Observamos el comportamiento de la expresion cerca de ese punto y, con el analisis simbolico verificado, el limite resulta ser {result}."
            )

        if parsed.problem_type.value == "integral":
            variable = cls._math_inline(parsed.variable or "x")
            return (
                f"Buscamos una antiderivada de {expression} respecto de {variable}. "
                f"Al integrar la expresion obtenemos {result}. "
                "Si quieres, en el siguiente mensaje te lo desarrollo paso a paso."
            )

        if parsed.problem_type.value == "derivative":
            variable = cls._math_inline(parsed.variable or "x")
            return (
                f"Derivamos la funcion {expression} con respecto a {variable}. "
                f"El resultado verificado es {result}. "
                "Si quieres, te muestro como se aplica la regla correspondiente paso a paso."
            )

        if parsed.problem_type.value == "equation":
            return (
                f"Tomamos la ecuacion {expression} y despejamos la variable indicada. "
                f"La solucion obtenida es {result}."
            )

        return (
            f"Trabajamos con la expresion {expression} y la simplificamos de forma simbolica. "
            f"El resultado obtenido es {result}."
        )

    @staticmethod
    def _should_use_llm(student_request: str | None) -> bool:
        if not student_request:
            return False
        lowered = student_request.lower()
        return any(
            keyword in lowered
            for keyword in (
                "explica",
                "explicame",
                "explícame",
                "paso a paso",
                "procedimiento",
                "por que",
                "por qué",
                "demuestra",
                "justifica",
            )
        )

    @classmethod
    def _math_inline(cls, expression: str) -> str:
        return f"\\({cls._plain_to_latex(expression)}\\)"

    @staticmethod
    def _plain_to_latex(expression: str) -> str:
        return (
            expression.strip()
            .replace("**", "^")
            .replace("pi", r"\pi")
            .replace("oo", r"\infty")
            .replace("sin", r"\sin")
            .replace("cos", r"\cos")
            .replace("tan", r"\tan")
            .replace("sqrt", r"\sqrt")
            .replace("->", r"\to ")
            .replace("*", " ")
        )

    @staticmethod
    def _build_prompt(
        *,
        parsed: ParsedExercise,
        solved: SolvedExerciseData,
        student_request: str | None = None,
    ) -> str:
        steps = "\n".join(f"{index}. {step}" for index, step in enumerate(solved.steps, start=1))
        return f"""
Problema detectado: {parsed.problem_type.value}
Expresion extraida: {parsed.expression}
Variable: {parsed.variable or "no especificada"}
Punto del limite: {parsed.limit_point or "no aplica"}
Entrada interpretada por SymPy: {solved.sympy_input}
Resultado final: {solved.final_result}
Peticion actual del estudiante: {student_request or "No especificada"}
Pasos base del sistema:
{steps}

Redacta una explicacion en espanol con estas reglas:
- Usa los pasos base del sistema como unica fuente de verdad.
- Empieza explicando la idea principal con lenguaje natural.
- Desarrolla el procedimiento paso a paso, pero sin sonar robotico.
- Si ayuda, menciona por que se aplica esa regla o metodo.
- Cierra con el resultado final de manera breve.
- No uses encabezados rigidos ni asteriscos decorativos.
- Para expresiones matematicas y resultados usa LaTeX simple con delimitadores \\(...\\) o \\[...\\].
- Si aparece una fraccion, escribela como \\frac{{a}}{{b}}.
- No inventes nuevos calculos ni cambies el resultado.
- No corrijas ni pongas en duda el resultado del sistema.
- No propongas metodos alternativos si llevan a una discusion distinta del resultado final.
""".strip()

    @staticmethod
    def _normalize_llm_text(text: str) -> str:
        return normalize_llm_math_text(text)
