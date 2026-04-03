from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    KnowledgeSearchResult,
    normalize_search_text,
)
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
    _course_overview_request_stems = (
        "explic",
        "saber",
        "cont",
        "habl",
        "mostr",
        "resum",
        "repas",
    )
    _generic_course_tokens = {"calculo", "1", "2", "metodos", "numericos"}
    _robotic_scope_markers = (
        "no tengo registro de",
        "contexto previo",
        "hablar o explorar",
        "en este espacio",
        "estoy aqui para ayudarte",
        "listo para empezar nuestra conversacion",
        "tema especifico que debamos discutir",
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
            "Eres un tutor de calculo y metodos numericos. "
            "Hablas como una persona real: claro, cercano y directo. "
            "Mantienes el foco en matematicas. "
            "Usa el contexto reciente solo si realmente ayuda, pero no hables del historial, del corpus ni de reglas internas. "
            "Explica primero la idea central y luego desarrolla solo lo necesario para que se entienda. "
            "Usa ejemplos cortos cuando ayuden. "
            "Evita cierres obligatorios, saludos ceremoniosos y frases de plantilla como 'entiendo que...' o 'no tengo registro de...'. "
            "Si falta un dato importante, pide una sola aclaracion breve."
        )
        self.open_math_system_prompt = (
            "Eres un tutor de calculo y metodos numericos. "
            "Conversas con naturalidad, sin sonar como documento ni como bot. "
            "Mantienes la conversacion dentro del ambito matematico y rediriges con tacto si hace falta. "
            "Si el mensaje es muy abierto, responde con una invitacion breve a plantear una duda concreta de calculo o metodos numericos, "
            "sin decir que falta contexto previo. "
            "Si la pregunta es ambigua pero matematica, pide una sola aclaracion corta. "
            "No uses encabezados ni markdown decorativo. "
            "Usa un ejemplo corto solo cuando aporte. "
            "No cierres con una pregunta por obligacion."
        )

    def answer(
        self,
        question: str,
        *,
        conversation_context: list[str] | None = None,
    ) -> TopicExplanationResult:
        if not self.ollama_client:
            raise RuntimeError("OllamaClient no esta configurado.")

        course_hint = self.knowledge_base_service.detect_course_hint(question)
        references = self.knowledge_base_service.search(
            question,
            limit=self.settings.rag_top_k,
        )

        if course_hint and self._is_course_overview_query(
            question=question,
            course_hint=course_hint,
            references=references,
        ):
            return self._answer_course_overview(
                question=question,
                course=course_hint,
                conversation_context=conversation_context or [],
            )

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
        history_block = ""
        if conversation_context:
            history = "\n".join(conversation_context)
            history_block = f"Contexto reciente de la conversacion:\n{history}\n"
        return f"""
{history_block}
Pregunta del estudiante:
{question}

Contexto recuperado del corpus:
{context}

Responde como tutor humano.
- Usa el material recuperado como base, pero redacta de forma conversacional.
- Si el contexto reciente ayuda, conectalo con naturalidad sin mencionarlo explicitamente.
- Explica la idea principal primero y desarrolla solo lo necesario.
- Incluye un ejemplo corto solo si realmente aclara el concepto.
- Mantente idealmente por debajo de 150 palabras, salvo que el tema pida un poco mas.
- No menciones el corpus, el historial ni reglas internas.
- No cierres con una pregunta por obligacion.
""".strip()

    @staticmethod
    def _build_open_math_prompt(question: str, conversation_context: list[str]) -> str:
        history_block = ""
        if conversation_context:
            history = "\n".join(conversation_context)
            history_block = f"Contexto reciente de la conversacion:\n{history}\n"
        return f"""
{history_block}
Mensaje del estudiante:
{question}

Responde como tutor humano.
- Mantente en calculo y metodos numericos.
- Si el mensaje es una apertura o es muy general, invita de forma breve a plantear una duda concreta del curso.
- Si la pregunta es ambigua pero parece matematica, pide una sola aclaracion corta.
- Si el estudiante cambia de tema dentro de matematicas, adaptate sin remarcarlo.
- Mantente conciso y natural.
- No menciones "contexto previo", "historial" ni frases de asistente formales.
- No cierres con una pregunta por obligacion.
""".strip()

    @staticmethod
    def _build_course_overview_prompt(
        question: str,
        course: str,
        outline: list[tuple[str, list[str]]],
        conversation_context: list[str],
    ) -> str:
        history_block = ""
        if conversation_context:
            history = "\n".join(conversation_context)
            history_block = f"Contexto reciente de la conversacion:\n{history}\n"
        blocks = []
        for unit, topics in outline:
            formatted_topics = ", ".join(topic.replace("_", " ") for topic in topics)
            blocks.append(f"- {unit.replace('_', ' ')}: {formatted_topics}")
        outline_text = "\n".join(blocks)
        return f"""
{history_block}
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
- Puedes cerrar invitando a escoger el siguiente tema solo si se siente natural.
- No recites el esquema de forma mecanica.
- Evita markdown decorativo y encabezados rigidos.
""".strip()

    @classmethod
    def _normalize_llm_text(cls, text: str) -> str:
        normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        normalized = re.sub(r"^\* ", "- ", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = normalized.strip()
        return cls._soften_robotic_scope_reply(normalized)

    @classmethod
    def _soften_robotic_scope_reply(cls, text: str) -> str:
        normalized = normalize_search_text(text)
        marker_hits = sum(marker in normalized for marker in cls._robotic_scope_markers)
        if marker_hits < 2:
            return text

        return (
            "Puedo ayudarte con calculo y metodos numericos. "
            "Dime que tema, metodo o ejercicio quieres revisar y lo vemos paso a paso."
        )

    @classmethod
    def _is_course_overview_query(
        cls,
        *,
        question: str,
        course_hint: str,
        references: list[KnowledgeSearchResult],
    ) -> bool:
        normalized = normalize_search_text(question)
        if any(pattern in normalized for pattern in cls._course_overview_patterns):
            return True

        if not course_hint:
            return False

        if not any(stem in normalized for stem in cls._course_overview_request_stems):
            return False

        if not references:
            return True

        matched_terms = set(references[0].matched_terms)
        if not matched_terms:
            return True

        return matched_terms.issubset(cls._generic_course_tokens)
