"""
FastAPI-зависимости.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends

from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork
from app.repositories.system.session import SessionRepository

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


def get_session_read_repo(uow: UnitOfWork = Depends(get_uow)) -> SessionRepository:
    return SessionRepository(uow.session)


# def get_role_repo(uow: UnitOfWork = Depends(get_uow)) -> RoleRepository:
#     return RoleRepository(uow.session)
