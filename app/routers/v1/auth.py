from fastapi import APIRouter, Cookie, Depends, Request, Response, status

from app.core.security import SESSION_COOKIE_NAME, SESSION_MAX_AGE
from app.repositories.deps import get_session_repo, get_user_repo, get_user_role_repo
from app.repositories.system.session import SessionRepository
from app.repositories.system.user import UserRepository
from app.repositories.system.user_role import UserRoleRepository
from app.schemas.system import AuthLoginRequest, UserResponse
from app.use_cases import authenticate_user, logout_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/login/email", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_by_email(
    data: AuthLoginRequest,
    response: Response,
    request: Request,
    users: UserRepository = Depends(get_user_repo),
    sessions: SessionRepository = Depends(get_session_repo),
    user_roles: UserRoleRepository = Depends(get_user_role_repo),
) -> UserResponse:
    # Проверка активной сессии
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    auth_data = await authenticate_user(
        data.email,
        data.password,
        user_agent=data.user_agent,
        ip_address=data.ip_address,
        session_token=session_token,
        sessions=sessions,
        users=users,
        user_roles=user_roles,
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=auth_data.session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )
    return UserResponse(id=auth_data.id, name=auth_data.name, email=auth_data.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    sessions: SessionRepository = Depends(get_session_repo),
) -> None:
    if session_token:
        await logout_user(
            session_token,
            sessions=sessions,
        )
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )
