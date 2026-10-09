from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import Organization, User, UserOrganization

URL = "/api/organizations"

ITEM_KEYS = {"id", "owner_id", "name", "inn", "address", "created_at", "updated_at"}

MakeOrganization = Callable[..., Awaitable[Organization]]
MakeUserOrganization = Callable[[User, Organization], Awaitable[UserOrganization]]


def _ids(body: list[dict[str, Any]]) -> set[str]:
    """Collect organization ids from the response body.

    Собирает id организаций из тела ответа.
    """
    return {item["id"] for item in body}


# ─────────────────────────────────────────────────────────────
# 200 — результаты
# ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "address",
    [
        pytest.param("г. Москва", id="with_address"),
        pytest.param(None, id="address_none"),
    ],
)
async def test_get_organizations_one(
    authorized_client: AsyncClient,
    user: User,
    make_organization: MakeOrganization,
    make_user_organization: MakeUserOrganization,
    address: str | None,
) -> None:
    """One linked organization -> a single item with all fields filled.

    Одна связанная организация -> один элемент со всеми полями.
    """
    org = await make_organization(owner=user, address=address)
    await make_user_organization(user, org)

    response = await authorized_client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    item = body[0]
    assert set(item) == ITEM_KEYS
    assert item["id"] == str(org.id)
    assert item["owner_id"] == str(user.id)
    assert item["name"] == org.name
    assert item["inn"] == org.inn
    assert item["address"] == address
    assert datetime.fromisoformat(item["created_at"]) == org.created_at
    assert datetime.fromisoformat(item["updated_at"]) == org.updated_at


async def test_get_organizations_several(
    authorized_client: AsyncClient,
    user: User,
    organizations: list[Organization],
    make_user_organization: MakeUserOrganization,
) -> None:
    """Several linked organizations -> all returned, order is not guaranteed.

    Несколько связанных организаций -> возвращаются все, порядок не гарантирован.
    """
    for org in organizations:
        await make_user_organization(user, org)

    response = await authorized_client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == len(organizations)
    assert _ids(body) == {str(o.id) for o in organizations}


async def test_get_organizations_empty(authorized_client: AsyncClient, user: User) -> None:
    """User without organizations (and without permissions) -> 200 and [].

    Пользователь без организаций (и без прав) -> 200 и [].
    """
    response = await authorized_client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


async def test_get_organizations_isolated(
    authorized_client: AsyncClient,
    user: User,
    users: list[User],
    make_organization: MakeOrganization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Organizations of another user are not returned.

    Организации другого пользователя в ответ не попадают.
    """
    other = users[0]
    own = await make_organization(owner=user)
    foreign = await make_organization(owner=other)
    await make_user_organization(user, own)
    await make_user_organization(other, foreign)

    response = await authorized_client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert _ids(body) == {str(own.id)}
    assert str(foreign.id) not in _ids(body)


async def test_get_organizations_member_of_foreign(
    authorized_client: AsyncClient,
    user: User,
    users: list[User],
    make_organization: MakeOrganization,
    make_user_organization: MakeUserOrganization,
) -> None:
    """Selection goes by link, not ownership: a foreign organization is returned.

    Выборка идёт по связи, а не по владению: чужая организация, где
    пользователь участник, возвращается.
    """
    other = users[0]
    foreign = await make_organization(owner=other)
    await make_user_organization(user, foreign)

    response = await authorized_client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert [(i["id"], i["owner_id"]) for i in body] == [(str(foreign.id), str(other.id))]


# ─────────────────────────────────────────────────────────────
# 401 — неаутентифицирован
# ─────────────────────────────────────────────────────────────


async def test_get_organizations_no_cookie(client: AsyncClient) -> None:
    """No session cookie -> 401.

    Без cookie сессии -> 401.
    """
    response = await client.get(URL)

    assert response.status_code == 401


async def test_get_organizations_invalid_cookie(client: AsyncClient) -> None:
    """Unknown session token -> 401.

    Неизвестный токен сессии -> 401.
    """
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")

    response = await client.get(URL)

    assert response.status_code == 401


async def test_get_organizations_expired_session(
    client: AsyncClient,
    user: User,
    session: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    """Expired session -> 401.

    Истёкшая сессия -> 401.
    """
    session["data"].expires_at = datetime.now(UTC) - timedelta(days=1)
    await db_session.flush()
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])

    response = await client.get(URL)

    assert response.status_code == 401


async def test_get_organizations_inactive_user(
    client: AsyncClient,
    session_for_inactive_user: dict[str, Any],
) -> None:
    """Valid session of an inactive user -> 401.

    Валидная сессия неактивного пользователя -> 401.
    """
    client.cookies.set(SESSION_COOKIE_NAME, session_for_inactive_user["token"])

    response = await client.get(URL)

    assert response.status_code == 401
