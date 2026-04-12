from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


def build_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)()


def build_service(**overrides) -> AuthService:
    settings = SimpleNamespace(
        auth_session_ttl_hours=24,
        teacher_access_code="teacher-secret",
        **overrides,
    )
    return AuthService(settings=settings)


def test_register_student_creates_account_and_session() -> None:
    db = build_session()
    service = build_service()

    result = service.register(
        db=db,
        payload=RegisterRequest(
            display_name="Ana Martinez",
            email="ana@universidad.edu",
            password="Segura123",
            role="student",
        ),
    )

    assert result.user.email == "ana@universidad.edu"
    assert result.user.role == "student"
    assert result.access_token
    assert db.query(User).count() == 1


def test_register_teacher_requires_valid_access_code() -> None:
    db = build_session()
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        service.register(
            db=db,
            payload=RegisterRequest(
                display_name="Docente Uno",
                email="docente@universidad.edu",
                password="Segura123",
                role="teacher",
                teacher_access_code="incorrecto",
            ),
        )

    assert exc_info.value.status_code == 403


def test_login_returns_new_session_for_existing_user() -> None:
    db = build_session()
    service = build_service()
    service.register(
        db=db,
        payload=RegisterRequest(
            display_name="Carlos Ramirez",
            email="carlos@universidad.edu",
            password="Segura123",
            role="student",
        ),
    )
    db.commit()

    result = service.login(
        db=db,
        payload=LoginRequest(email="carlos@universidad.edu", password="Segura123"),
    )

    assert result.user.display_name == "Carlos Ramirez"
    assert result.access_token


def test_get_user_from_token_returns_authenticated_user() -> None:
    db = build_session()
    service = build_service()
    response = service.register(
        db=db,
        payload=RegisterRequest(
            display_name="Laura Gomez",
            email="laura@universidad.edu",
            password="Segura123",
            role="student",
        ),
    )
    db.commit()

    user = service.get_user_from_token(db=db, token=response.access_token)

    assert user.email == "laura@universidad.edu"


def test_logout_revokes_session() -> None:
    db = build_session()
    service = build_service()
    response = service.register(
        db=db,
        payload=RegisterRequest(
            display_name="Profesor Uno",
            email="profe@universidad.edu",
            password="Segura123",
            role="teacher",
            teacher_access_code="teacher-secret",
        ),
    )
    db.commit()

    service.logout(db=db, token=response.access_token)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        service.get_user_from_token(db=db, token=response.access_token)

    assert exc_info.value.status_code == 401
