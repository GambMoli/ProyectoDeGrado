from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.services.auth_service import AuthService
from app.services.conversation_planner_service import ConversationPlannerService
from app.services.conversation_orchestrator_service import ConversationOrchestratorService
from app.services.conversation_service import ConversationService
from app.services.explanation_service import ExplanationService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.math_parser_service import MathParserService
from app.services.ocr_service import build_ocr_service
from app.services.ollama_client import OllamaClient
from app.services.practice_service import PracticeService
from app.services.reports_service import ReportsService
from app.services.response_composer_service import ResponseComposerService
from app.services.sympy_solver_service import SymPySolverService
from app.services.topic_explanation_service import TopicExplanationService

security = HTTPBearer(auto_error=False)


@lru_cache
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(get_settings())


@lru_cache
def get_conversation_service() -> ConversationService:
    settings = get_settings()
    repository = ConversationRepository()
    parser_service = MathParserService()
    solver_service = SymPySolverService()
    ocr_service = build_ocr_service(settings)
    knowledge_base_service = KnowledgeBaseService(settings.knowledge_datasets_dir)
    ollama_client = OllamaClient(settings)
    explanation_service = ExplanationService(settings, ollama_client)
    practice_service = PracticeService(
        settings=settings,
        parser_service=parser_service,
        solver_service=solver_service,
        ollama_client=ollama_client,
        knowledge_base_service=knowledge_base_service,
    )
    conversation_planner_service = ConversationPlannerService(
        settings=settings,
        knowledge_base_service=knowledge_base_service,
        parser_service=parser_service,
        ollama_client=ollama_client,
    )
    conversation_orchestrator_service = ConversationOrchestratorService(
        settings=settings,
        ollama_client=ollama_client,
        parser_service=parser_service,
    )
    response_composer_service = ResponseComposerService(settings, ollama_client)
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
        conversation_orchestrator_service=conversation_orchestrator_service,
        conversation_planner_service=conversation_planner_service,
        response_composer_service=response_composer_service,
        topic_explanation_service=topic_explanation_service,
    )


@lru_cache
def get_reports_service() -> ReportsService:
    return ReportsService()


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesion para continuar.",
        )
    return credentials.credentials


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_current_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.get_user_from_token(db=db, token=token)


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los profesores pueden acceder a reportes.",
        )
    return current_user


__all__ = [
    "Session",
    "get_auth_service",
    "get_current_teacher",
    "get_current_token",
    "get_current_user",
    "get_db",
    "get_conversation_service",
    "get_reports_service",
    "get_settings_dependency",
]
