"""
FastAPI-зависимости.
"""

from collections.abc import AsyncGenerator

from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork

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


# def get_base_repo(uow: UnitOfWork = Depends(get_uow)) -> BaseRepository:
#     return BaseRepository(uow.session)


# def get_role_repo(uow: UnitOfWork = Depends(get_uow)) -> RoleRepository:
#     return RoleRepository(uow.session)
