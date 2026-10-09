from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import Organization, User, UserOrganization

URL = "/api/organizations"


@pytest.mark.asyncio
async def test_create_organization_success(
    authorized_client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Create an organization and validate the response contract.

    Создать организацию и проверить контракт ответа.
    """
    payload = {
        "name": "ООО Ромашка",
        "inn": "770708389311",
        "address": "г. Москва, ул. Примерная, д. 1",
    }

    response = await authorized_client.post(URL, json=payload)

    assert response.status_code == 201
    body = response.json()

    assert set(body) == {
        "id",
        "owner_id",
        "name",
        "inn",
        "address",
        "created_at",
        "updated_at",
    }

    organization_id = UUID(body["id"])

    assert body["owner_id"] == str(user.id)
    assert body["name"] == payload["name"]
    assert body["inn"] == payload["inn"]
    assert body["address"] == payload["address"]

    organization = await db_session.scalar(
        select(Organization).where(Organization.id == organization_id)
    )

    assert organization is not None
    assert organization.owner_id == user.id
    assert organization.name == payload["name"]
    assert organization.inn == payload["inn"]
    assert organization.address == payload["address"]


@pytest.mark.asyncio
async def test_create_organization_creates_user_link(
    authorized_client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Create a user-organization association.

    Создать связь пользователя с организацией.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": "ООО Связь с владельцем",
            "inn": "770708389311",
            "address": "г. Москва",
        },
    )

    assert response.status_code == 201
    organization_id = UUID(response.json()["id"])

    link = await db_session.scalar(
        select(UserOrganization).where(
            UserOrganization.user_id == user.id,
            UserOrganization.organization_id == organization_id,
        )
    )

    assert link is not None
    assert link.user_id == user.id
    assert link.organization_id == organization_id


@pytest.mark.asyncio
async def test_created_organization_is_visible_in_get(
    authorized_client: AsyncClient,
    user: User,
) -> None:
    """Verify that the created organization appears in GET /organizations.

    Проверить, что созданная организация отображается в GET /organizations.
    """
    payload = {
        "name": "ООО Видимая организация",
        "inn": "500100732259",
        "address": "г. Москва",
    }

    create_response = await authorized_client.post(URL, json=payload)

    assert create_response.status_code == 201
    created = create_response.json()

    get_response = await authorized_client.get(URL)

    assert get_response.status_code == 200

    organizations = get_response.json()
    organization = next(
        (item for item in organizations if item["id"] == created["id"]),
        None,
    )

    assert organization is not None
    assert organization["owner_id"] == str(user.id)
    assert organization["name"] == payload["name"]
    assert organization["inn"] == payload["inn"]
    assert organization["address"] == payload["address"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty_name"),
        pytest.param("   ", id="whitespace_only_name"),
        pytest.param("А" * 256, id="name_too_long"),
    ],
)
async def test_create_organization_rejects_invalid_name(
    authorized_client: AsyncClient,
    name: str,
) -> None:
    """Reject an empty, whitespace-only, or oversized name.

    Отклонить пустое название, строку из пробелов или слишком длинное название.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": name,
            "inn": "7707083893",
            "address": "г. Москва",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "inn",
    [
        pytest.param("", id="empty_inn"),
        pytest.param("abcdefghij", id="letters"),
        pytest.param("770708389", id="nine_digits"),
        pytest.param("77070838931", id="eleven_digits"),
        pytest.param("5001007322591", id="twelve_digits"),
        pytest.param("7707-083893", id="hyphen"),
        pytest.param("77070 83893", id="embedded_whitespace"),
    ],
)
async def test_create_organization_rejects_invalid_inn(
    authorized_client: AsyncClient,
    inn: str,
) -> None:
    """Reject an INN that does not contain exactly ten digits.

    Отклонить ИНН, который не состоит ровно из 12 цифр.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": "ООО Некорректный ИНН",
            "inn": inn,
            "address": "г. Москва",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_organization_rejects_missing_inn(
    authorized_client: AsyncClient,
) -> None:
    """Reject a request without the required INN.

    Отклонить запрос без обязательного ИНН.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": "ООО Без ИНН",
            "address": "г. Москва",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_organization_without_address(
    authorized_client: AsyncClient,
) -> None:
    """Create an organization without the optional address.

    Создать организацию без необязательного адреса.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": "ООО Без адреса",
            "inn": "770708389311",
        },
    )

    assert response.status_code == 201
    assert response.json()["address"] is None


@pytest.mark.asyncio
async def test_create_organization_without_cookie(
    client: AsyncClient,
) -> None:
    """Reject a request without a session cookie.

    Отклонить запрос без cookie сессии.
    """
    response = await client.post(
        URL,
        json={
            "name": "ООО Без сессии",
            "inn": "770708389311",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_organization_invalid_cookie(
    client: AsyncClient,
) -> None:
    """Reject a request with an invalid session cookie.

    Отклонить запрос с невалидной cookie сессии.
    """
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")

    response = await client.post(
        URL,
        json={
            "name": "ООО Невалидная сессия",
            "inn": "770708389311",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_organization_inactive_user(
    client: AsyncClient,
    session_for_inactive_user: dict[str, Any],
) -> None:
    """Reject a request from an inactive user.

    Отклонить запрос неактивного пользователя.
    """
    client.cookies.set(
        SESSION_COOKIE_NAME,
        session_for_inactive_user["token"],
    )

    response = await client.post(
        URL,
        json={
            "name": "ООО Неактивный пользователь",
            "inn": "770708389311",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_organization_duplicate_inn(
    authorized_client: AsyncClient,
    organization: Organization,
) -> None:
    """Reject an organization with an existing INN.

    Отклонить создание организации с уже существующим ИНН.
    """
    response = await authorized_client.post(
        URL,
        json={
            "name": "ООО Дубликат ИНН",
            "inn": organization.inn,
            "address": "г. Москва",
        },
    )

    assert response.status_code == 409
