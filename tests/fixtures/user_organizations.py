from collections.abc import Awaitable, Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Organization, User, UserOrganization


@pytest_asyncio.fixture
async def make_user_organization(
    db_session: AsyncSession,
) -> Callable[[User, Organization], Awaitable[UserOrganization]]:
    """Factory of user <-> organization links.

    Фабрика связей user <-> organization.
    """

    async def _make(user: User, organization: Organization) -> UserOrganization:
        link = UserOrganization(user_id=user.id, organization_id=organization.id)
        db_session.add(link)
        await db_session.flush()
        return link

    return _make
