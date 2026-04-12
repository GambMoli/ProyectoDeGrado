from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_auth_service,
    get_current_token,
    get_current_user,
    get_db,
)
from app.models.user import User
from app.schemas.auth import AuthResponse, AuthUserOut, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    response = auth_service.register(db=db, payload=payload)
    db.commit()
    return response


@router.post("/auth/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    response = auth_service.login(db=db, payload=payload)
    db.commit()
    return response


@router.get("/auth/me", response_model=AuthUserOut)
def get_me(current_user: User = Depends(get_current_user)) -> AuthUserOut:
    return AuthUserOut(
        id=current_user.id,
        display_name=current_user.display_name,
        email=current_user.email or "",
        role=current_user.role,
        is_anonymous=current_user.is_anonymous,
        created_at=current_user.created_at,
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(get_current_token),
) -> Response:
    auth_service.logout(db=db, token=token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
