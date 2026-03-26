from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services.knowledge_base_service import KnowledgeBaseService, KnowledgeSearchResult
from app.services.ollama_client import OllamaClient, OllamaClientError

if TYPE_CHECKING:
    from app.core.config import Settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TopicExplanationResult:
    text: str
    source: str
    references: list[KnowledgeSearchResult]


class TopicExplanationService:
    _course_overview_patterns = (
        "que sabes de",
        "que incluye",
        "que temas",
        "temas de",
        "unidades de",
        "contenido de",
        "programa de",
        "de que trata",
    )

    def __init__(
        self,
        settings: Settings,
        knowledge_base_service: KnowledgeBaseService,
        ollama_client: OllamaClient | None = None,
    ) -> None:
        self.settings = settings
        self.knowledge_base_service = knowledge_base_service
        self.ollama_client = ollama_client
        self.rag_system_prompt = (
            "Eres un tutor academico de calculo y metodos numericos. "
            "REGLAS QUE DEBES SEGUIR SIEMPRE: "
            "1. Responde SOLO sobre el tema especifico que menciona el estudiante en su ultimo mensaje. "
            "2. Estructura tu respuesta asi: primero la idea principal en 1-2 oraciones claras, "
            "luego desarrolla brevemente con un ejemplo concreto si aplica. "
            "3. Se conciso: maximo 150 palabras por respuesta, salvo que el tema sea genuinamente complejo. "
            "4. Al final, haz UNA sola pregunta corta para verificar que el estudiante entendio. "
            "5. Usa la informacion del corpus como base principal. No inventes teoria fuera de ese contexto. "
            "6. No uses encabezados rigidos, asteriscos dobles, markdown decorativo ni tono de plantilla. "
            "7. Si la pregunta no es clara, pide UNA aclaracion corta antes de responder."
        )
        self.open_math_system_prompt = (
            "Eres un tutor academico de calculo y metodos numericos. "
            "REGLAS QUE DEBES SEGUIR SIEMPRE: "
            "1. Responde SOLO la pregunta concreta del estudiante. No agregues temas que no pidio. "
            "2. Una respuesta = un solo tema. No mezcles conceptos no solicitados. "
            "3. Se conciso: maximo 150 palabras salvo que el tema genuinamente lo requiera. "
            "4. Si la pregunta es vaga o ambigua, pide clarificacion ANTES de responder. "
            "5. Si la pregunta no es de matematicas, redirige amablemente al ambito matematico. "
            "6. No uses encabezados, asteriscos dobles ni markdown decorativo. "
            "7. Incluye un ejemplo numerico corto cuando sea util para la explicacion. "
            "8. Habla como tutor cercano, no como documento tecnico. "
            "9. Al final, haz una pregunta corta de verificacion."
        )

    def answer(
        self,
        question: str,
        *,
        conversation_context: list[str] | None = None,
    ) -> TopicExplanationResult:
        course_hint = self.knowledge_base_service.detect_course_hint(question)
        if course_hint and self._is_course_overview_query(question):
            return self._answer_course_overview(
                question=question,
                course=course_hint,
                conversation_context=conversation_context or [],
            )

        references = self.knowledge_base_service.search(
            question,
            limit=self.settings.rag_top_k,
        )

        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        if references:
            prompt = self._build_rag_prompt(
                question=question,
                references=references,
                conversation_context=conversation_context or [],
            )
            system_prompt = self.rag_system_prompt
            source = "ollama_rag"
        else:
            prompt = self._build_open_math_prompt(
                question=question,
                conversation_context=conversation_context or [],
            )
            system_prompt = self.open_math_system_prompt
            source = "ollama_math_chat"
            
        text = self.ollama_client.generate(
            system_prompt=system_prompt,
            prompt=prompt,
        )
        return TopicExplanationResult(
            text=self._normalize_llm_text(text),
            source=source,
            references=references,
        )

    def _answer_course_overview(
        self,
        *,
        question: str,
        course: str,
        conversation_context: list[str],
    ) -> TopicExplanationResult:
        course_documents = self.knowledge_base_service.get_course_documents(course)
        outline = self.knowledge_base_service.get_course_outline(course)

        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")
            
        if not outline:
            return TopicExplanationResult(
                text=(
                    f"Puedo ayudarte con {course.replace('_', ' ')}, "
                    "pero todavia no tengo un esquema suficiente cargado para resumirlo bien."
                ),
                source="course_outline_fallback",
                references=[],
            )

        prompt = self._build_course_overview_prompt(
            question=question,
            course=course,
            outline=outline,
            conversation_context=conversation_context,
        )
        text = self.ollama_client.generate(
            system_prompt=self.rag_system_prompt,
            prompt=prompt,
        )
        return TopicExplanationResult(
            text=self._normalize_llm_text(text),
            source="ollama_course_overview",
            references=[
                KnowledgeSearchResult(
                    document=document,
                    score=1.0,
                    matched_terms=[],
                )
                for document in course_documents[: self.settings.rag_top_k]
            ],
        )

    @staticmethod
    def _build_rag_prompt(
        question: str,
        references: list[KnowledgeSearchResult],
        conversation_context: list[str],
    ) -> str:
        context_blocks = []
        for index, reference in enumerate(references, start=1):
            doc = reference.document
            context_blocks.append(
                f"[{index}] Curso: {doc.course}\n"
                f"Unidad: {doc.unit}\n"
                f"Tema: {doc.topic}\n"
                f"Subtema: {doc.subtopic}\n"
                f"Texto base: {doc.text}"
            )
        context = "\n\n".join(context_blocks)
        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        return f"""
Contexto reciente de la conversacion:
{history}

Pregunta del estudiante:
{question}

Contexto recuperado del corpus:
{context}

INSTRUCCIONES ESTRICTAS:
1. Responde SOLO lo que pide el estudiante en su ultimo mensaje.
2. Si el estudiante evade tu pregunta anterior o cambia de tema abruptamente, AVANZA sin responderte a ti mismo.
3. Si el estudiante te pide explicitamente relacionar el tema anterior con uno nuevo, enlazalos con naturalidad.
4. Desarrolla la respuesta usando el contexto recuperado como base.
5. Incluye un ejemplo corto si aplica.
6. Maximo 150 palabras salvo que sea un tema muy complejo.
7. Termina con una pregunta corta de verificacion relacionada al tema actual.
8. Habla con naturalidad, como tutor humano. No uses markdown excesivo ni encabezados.
9. No inventes informacion fuera del contexto proporcionado.
""".strip()

    @staticmethod
    def _build_open_math_prompt(question: str, conversation_context: list[str]) -> str:
        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        return f"""
Contexto reciente de la conversacion:
{history}

Mensaje del estudiante:
{question}

INSTRUCCIONES ESTRICTAS:
1. Responde SOLO al ultimo mensaje del estudiante. Un tema principal por respuesta.
2. Si el usuario evade tu pregunta o cambia de tema repentinamente, sigue el nuevo tema y no te respondas a ti mismo.
3. Si el usuario pide enlazar un concepto anterior con uno nuevo, explicaselo conectando ambas ideas de forma cohesiva.
4. Maximo 150 palabras salvo que el tema lo requiera.
5. Pide clarificacion si falta un ejercicio concreto o datos.
6. Si no es un tema matematico, redirige amablemente.
7. Incluye un ejemplo corto cuando aplique.
8. Termina con una sola pregunta de verificacion.
9. No menciones corpus ni fuentes, actua como humano. No uses encabezados markdown.
""".strip()

    @staticmethod
    def _build_course_overview_prompt(
        question: str,
        course: str,
        outline: list[tuple[str, list[str]]],
        conversation_context: list[str],
    ) -> str:
        history = "\n".join(conversation_context) if conversation_context else "Sin contexto previo relevante."
        blocks = []
        for unit, topics in outline:
            formatted_topics = ", ".join(topic.replace("_", " ") for topic in topics)
            blocks.append(f"- {unit.replace('_', ' ')}: {formatted_topics}")
        outline_text = "\n".join(blocks)
        return f"""
Contexto reciente de la conversacion:
{history}

Pregunta del estudiante:
{question}

Curso consultado:
{course.replace('_', ' ')}

Esquema del curso:
{outline_text}

Responde como tutor humano.
- Resume de que trata el curso.
- Explica sus bloques principales con lenguaje natural.
- Menciona 1 o 2 ejemplos de lo que se aprende.
- Cierra preguntando en que tema quiere profundizar.
- No recites el esquema de forma mecanica.
- Evita markdown decorativo y encabezados rigidos.
""".strip()

    @staticmethod
    def _build_template_answer(question: str, references: list[KnowledgeSearchResult]) -> str:
        lead = (
            f"Para responder '{question}', encontre estos puntos relevantes en el corpus:\n"
        )
        body = "\n".join(
            f"- {reference.document.topic.replace('_', ' ')}: {reference.document.text}"
            for reference in references[:3]
        )
        sources = "\n".join(
            f"- {reference.document.course} / {reference.document.unit} / {reference.document.topic}"
            for reference in references[:3]
        )
        return (
            f"{lead}\n{body}\n\n"
            "Base consultada:\n"
            f"{sources}"
        )

    @staticmethod
    def _build_course_overview_template(
        *,
        course: str,
        outline: list[tuple[str, list[str]]],
    ) -> str:
        if not outline:
            return (
                f"Puedo ayudarte con {course.replace('_', ' ')}, "
                "pero todavia no tengo un esquema suficiente cargado para resumirlo bien."
            )

        unit_lines = []
        for unit, topics in outline:
            formatted_topics = ", ".join(topic.replace("_", " ") for topic in topics[:3])
            unit_lines.append(f"- {unit.replace('_', ' ')}: {formatted_topics}")

        joined_units = "\n".join(unit_lines)
        return (
            f"{course.replace('_', ' ').capitalize()} cubre varios bloques importantes.\n\n"
            "De forma general, estos son los temas base que tengo cargados:\n"
            f"{joined_units}\n\n"
            "Si quieres, puedo explicarte uno de esos bloques con mas detalle o ayudarte con un ejercicio puntual."
        )

    @staticmethod
    def _normalize_llm_text(text: str) -> str:
        normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        normalized = re.sub(r"^\* ", "- ", normalized, flags=re.MULTILINE)
        return normalized.strip()

    @classmethod
    def _is_course_overview_query(cls, question: str) -> bool:
        normalized = question.lower()
        return any(pattern in normalized for pattern in cls._course_overview_patterns)
