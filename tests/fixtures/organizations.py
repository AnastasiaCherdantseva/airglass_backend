from collections.abc import Awaitable, Callable
from datetime import datetime
from itertools import count
from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto import OrganizationData
from app.models.system import Organization, User


@pytest_asyncio.fixture
async def make_organization(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[Organization]]:
    """Organization factory. Unique name and INN are generated automatically.

    Фабрика организаций. Уникальные name и inn генерируются автоматически.
    """
    counter = count(1)

    async def _make(
        *,
        owner: User,
        name: str | None = None,
        inn: str | None = None,
        address: str | None = None,
        updated_at: datetime | None = None,
    ) -> Organization:
        n = next(counter)
        organization = Organization(
            id=uuid4(),
            owner_id=owner.id,
            name=name or f"Организация {n}",
            inn=inn or f"{n:010d}",
            address=address,
        )
        if updated_at is not None:
            organization.updated_at = updated_at
        db_session.add(organization)
        await db_session.flush()
        return organization

    return _make


@pytest_asyncio.fixture
async def organization(
    user: User,
    make_organization: Callable[..., Awaitable[Organization]],
) -> Organization:
    """One organization owned by `user`.

    Одна организация, владелец — `user`.
    """
    return await make_organization(owner=user, address="г. Москва")


@pytest_asyncio.fixture
async def organizations(
    user: User,
    make_organization: Callable[..., Awaitable[Organization]],
) -> list[Organization]:
    """Three organizations owned by `user`.

    Три организации одного владельца `user`.
    """
    return [await make_organization(owner=user) for _ in range(3)]


@pytest_asyncio.fixture
async def new_organization_data() -> OrganizationData:
    """DTO for create_for_user (nothing in the DB yet).

    DTO для create_for_user (в БД ещё ничего нет).
    """
    return OrganizationData(name="ООО Новая", inn="7701234567", address="г. Москва")
