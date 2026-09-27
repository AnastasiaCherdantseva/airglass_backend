from fastapi import APIRouter, Depends, Response, status

from app.repositories.deps import get_session_repo, get_user_repo, get_user_role_repo
from app.repositories.system.session import SessionRepository
from app.repositories.system.user import UserRepository
from app.repositories.system.user_role import UserRoleRepository
from app.schemas.system import AuthLoginRequest, UserResponse
from app.use_cases.system import authenticate_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
SESSION_COOKIE_NAME = "session_id"
SESSION_MAX_AGE = 7 * 24 * 3600


@router.post("/login/email", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_by_email(
    data: AuthLoginRequest,
    response: Response,
    users: UserRepository = Depends(get_user_repo),
    sessions: SessionRepository = Depends(get_session_repo),
    user_roles: UserRoleRepository = Depends(get_user_role_repo),
) -> UserResponse:
    auth_data = await authenticate_user(
        data.email,
        data.password,
        user_agent=data.user_agent,
        ip_address=data.ip_address,
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
    return UserResponse(
        id=auth_data.id, roles=auth_data.roles, name=auth_data.name, email=auth_data.email
    )
