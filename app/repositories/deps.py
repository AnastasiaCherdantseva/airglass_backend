"""
FastAPI-зависимости.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends

from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork
from app.repositories.system import (
    PermissionConditionRepository,
    PermissionRepository,
    RolePermissionRepository,
    RoleRepository,
    SessionRepository,
    UserDirectPermissionRepository,
    UserPermissionRepository,
    UserRepository,
    UserRoleRepository,
)


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


def get_role_repo(uow: UnitOfWork = Depends(get_uow)) -> RoleRepository:
    return RoleRepository(uow.session)


def get_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> PermissionRepository:
    return PermissionRepository(uow.session)


def get_permission_condition_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> PermissionConditionRepository:
    return PermissionConditionRepository(uow.session)


def get_user_role_repo(uow: UnitOfWork = Depends(get_uow)) -> UserRoleRepository:
    return UserRoleRepository(uow.session)


def get_role_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> RolePermissionRepository:
    return RolePermissionRepository(uow.session)


def get_user_direct_permission_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> UserDirectPermissionRepository:
    return UserDirectPermissionRepository(uow.session)


def get_user_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> UserPermissionRepository:
    return UserPermissionRepository(uow.session)
