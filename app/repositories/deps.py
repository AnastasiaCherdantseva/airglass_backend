"""
FastAPI-зависимости.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends

from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork
from app.repositories.system.session import SessionRepository
from app.repositories.system.user import UserRepository
from app.repositories.system.user_role import UserRoleRepository

# from app.repositories.role import RoleRepository


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with AsyncSessionLocal() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        except Exception:
            await uow.rollback()
            raise
        else:
            await uow.commit()


def get_session_repo(uow: UnitOfWork = Depends(get_uow)) -> SessionRepository:
    return SessionRepository(uow.session)


def get_user_repo(uow: UnitOfWork = Depends(get_uow)) -> UserRepository:
    return UserRepository(uow.session)


def get_user_role_repo(uow: UnitOfWork = Depends(get_uow)) -> UserRoleRepository:
    return UserRoleRepository(uow.session)
