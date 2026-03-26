from __future__ import annotations

from functools import lru_cache

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.services.conversation_service import ConversationService
from app.services.explanation_service import ExplanationService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.ocr_service import build_ocr_service
from app.services.ollama_client import OllamaClient
from app.services.practice_service import PracticeService
from app.services.sympy_solver_service import SymPySolverService
from app.services.topic_explanation_service import TopicExplanationService
from app.services.tutor_agent_service import TutorAgentService


@lru_cache
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache
def get_conversation_service() -> ConversationService:
    settings = get_settings()
    repository = ConversationRepository()
    parser_service = MathParserService()
    solver_service = SymPySolverService()
    ocr_service = build_ocr_service(settings)
    knowledge_base_service = KnowledgeBaseService(settings.knowledge_datasets_dir)
    ollama_client = OllamaClient(settings) if settings.ollama_enabled else None
    explanation_service = ExplanationService(settings, ollama_client)
    practice_service = PracticeService(
        settings=settings,
        parser_service=parser_service,
        solver_service=solver_service,
        ollama_client=ollama_client,
        knowledge_base_service=knowledge_base_service,
    )
    tutor_agent_service = TutorAgentService(
        settings=settings,
        knowledge_base_service=knowledge_base_service,
        parser_service=parser_service,
        ollama_client=ollama_client,
    )
    topic_explanation_service = TopicExplanationService(
        settings,
        knowledge_base_service,
        ollama_client,
    )
    return ConversationService(
        repository=repository,
        parser_service=parser_service,
        solver_service=solver_service,
        explanation_service=explanation_service,
        ocr_service=ocr_service,
        practice_service=practice_service,
        tutor_agent_service=tutor_agent_service,
        topic_explanation_service=topic_explanation_service,
    )


__all__ = ["Session", "get_db", "get_conversation_service", "get_settings_dependency"]
