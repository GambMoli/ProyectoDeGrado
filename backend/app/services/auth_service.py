from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.auth import AuthResponse, AuthUserOut, LoginRequest, RegisterRequest
from app.utils.security import (
    expires_in_hours,
    generate_session_token,
    hash_password,
    hash_session_token,
    utc_now,
    verify_password,
)


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def register(self, *, db: Session, payload: RegisterRequest) -> AuthResponse:
        email = payload.email.strip().lower()
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una cuenta registrada con ese correo.",
            )

        if payload.role == "teacher":
            self._validate_teacher_registration(payload.teacher_access_code)

        user = User(
            display_name=payload.display_name,
            email=email,
            password_hash=hash_password(payload.password),
            role=payload.role,
            is_anonymous=False,
        )
        db.add(user)
        db.flush()
        session = self._create_session(db=db, user=user)
        return self._build_auth_response(user=user, access_token=session["token"])

    def login(self, *, db: Session, payload: LoginRequest) -> AuthResponse:
        email = payload.email.strip().lower()
        user = db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña invalidos.",
            )

        session = self._create_session(db=db, user=user)
        return self._build_auth_response(user=user, access_token=session["token"])

    def get_user_from_token(self, *, db: Session, token: str) -> User:
        token_hash = hash_session_token(token)
        session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
            )
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesion invalida o expirada.",
            )

        if self._normalize_datetime(session.expires_at) <= utc_now():
            session.revoked_at = utc_now()
            db.add(session)
            db.flush()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La sesion ha expirado. Inicia sesion nuevamente.",
            )

        user = session.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se encontro el usuario asociado a la sesion.",
            )
        return user

    def logout(self, *, db: Session, token: str) -> None:
        token_hash = hash_session_token(token)
        session = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
        if not session:
            return
        session.revoked_at = utc_now()
        db.add(session)
        db.flush()

    def _create_session(self, *, db: Session, user: User) -> dict[str, str]:
        db.execute(
            delete(AuthSession).where(
                AuthSession.user_id == user.id,
                AuthSession.expires_at <= utc_now(),
            )
        )
        token = generate_session_token()
        auth_session = AuthSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=expires_in_hours(self.settings.auth_session_ttl_hours),
        )
        db.add(auth_session)
        db.flush()
        return {"token": token}

    def _validate_teacher_registration(self, teacher_access_code: str | None) -> None:
        expected_code = (self.settings.teacher_access_code or "").strip()
        if not expected_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El registro de profesores no esta habilitado.",
            )

        if (teacher_access_code or "").strip() != expected_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Codigo de acceso para profesor invalido.",
            )

    @staticmethod
    def _normalize_datetime(value):
        if value.tzinfo is None:
            return value.replace(tzinfo=utc_now().tzinfo)
        return value.astimezone(utc_now().tzinfo)

    @staticmethod
    def _build_auth_response(*, user: User, access_token: str) -> AuthResponse:
        return AuthResponse(
            access_token=access_token,
            user=AuthUserOut(
                id=user.id,
                display_name=user.display_name,
                email=user.email or "",
                role=user.role,
                is_anonymous=user.is_anonymous,
                created_at=user.created_at,
            ),
        )
