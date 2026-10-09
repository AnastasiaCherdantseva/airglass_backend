from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import Organization, User

URL = "/api/organizations"


async def test_patch_organization_name(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Update the organization name and preserve other fields.

    Обновить название организации и сохранить остальные поля.
    """
    original_inn = organization.inn
    original_address = organization.address
    new_name = "ООО Новое название"

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"name": new_name},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == str(organization.id)
    assert body["name"] == new_name
    assert body["inn"] == original_inn
    assert body["address"] == original_address

    await db_session.refresh(organization)

    assert organization.name == new_name
    assert organization.inn == original_inn
    assert organization.address == original_address


async def test_patch_organization_inn(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Update the organization INN.

    Обновить ИНН организации.
    """
    original_name = organization.name
    original_address = organization.address
    new_inn = "123456789012"

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"inn": new_inn},
    )

    assert response.status_code == 200, response.json()

    body = response.json()
    assert body["inn"] == new_inn
    assert body["name"] == original_name
    assert body["address"] == original_address

    await db_session.refresh(organization)

    assert organization.inn == new_inn
    assert organization.name == original_name
    assert organization.address == original_address


async def test_patch_organization_address(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Update the organization address.

    Обновить адрес организации.
    """
    original_name = organization.name
    original_inn = organization.inn
    new_address = "г. Санкт-Петербург, Невский проспект, д. 10"

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"address": new_address},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["address"] == new_address
    assert body["name"] == original_name
    assert body["inn"] == original_inn

    await db_session.refresh(organization)

    assert organization.address == new_address
    assert organization.name == original_name
    assert organization.inn == original_inn


async def test_patch_organization_multiple_fields(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Update multiple organization fields in one request.

    Обновить несколько полей организации одним запросом.
    """
    payload = {
        "name": "ООО Обновлённая организация",
        "inn": "234567890123",
        "address": "г. Казань, ул. Тестовая, д. 5",
    }

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["name"] == payload["name"]
    assert body["inn"] == payload["inn"]
    assert body["address"] == payload["address"]

    await db_session.refresh(organization)

    assert organization.name == payload["name"]
    assert organization.inn == payload["inn"]
    assert organization.address == payload["address"]


async def test_patch_organization_null_address_is_ignored(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Preserve the address when null is ignored by the use case.

    Сохранить адрес, поскольку use case игнорирует значение null.
    """
    original_address = organization.address

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"address": None},
    )

    assert response.status_code == 200
    assert response.json()["address"] == original_address

    await db_session.refresh(organization)

    assert organization.address == original_address


async def test_patch_organization_empty_body(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Return the organization unchanged for an empty patch.

    Вернуть организацию без изменений при пустом PATCH-запросе.
    """
    original_name = organization.name
    original_inn = organization.inn
    original_address = organization.address

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["name"] == original_name
    assert body["inn"] == original_inn
    assert body["address"] == original_address

    await db_session.refresh(organization)

    assert organization.name == original_name
    assert organization.inn == original_inn
    assert organization.address == original_address


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty_name"),
        pytest.param("   ", id="whitespace_only_name"),
        pytest.param("А" * 256, id="name_too_long"),
    ],
)
async def test_patch_organization_invalid_name(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
    name: str,
) -> None:
    """Reject an invalid organization name without changing the database.

    Отклонить некорректное название организации без изменения БД.
    """
    original_name = organization.name

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"name": name},
    )

    assert response.status_code == 422

    await db_session.refresh(organization)
    assert organization.name == original_name


@pytest.mark.parametrize(
    "inn",
    [
        pytest.param("abcdefghijkl", id="letters"),
        pytest.param("12345678901", id="eleven_digits"),
        pytest.param("1234567890123", id="thirteen_digits"),
        pytest.param("123456 78901", id="embedded_whitespace"),
    ],
)
async def test_patch_organization_invalid_inn(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
    inn: str,
) -> None:
    """Reject an invalid INN without changing the database.

    Отклонить некорректный ИНН без изменения БД.
    """
    original_inn = organization.inn

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"inn": inn},
    )

    assert response.status_code == 422

    await db_session.refresh(organization)
    assert organization.inn == original_inn


async def test_patch_organization_not_found(
    authorized_client: AsyncClient,
) -> None:
    """Return 404 when the organization does not exist.

    Вернуть 404, если организация не существует.
    """
    response = await authorized_client.patch(
        f"{URL}/{uuid4()}",
        json={"name": "ООО Новое название"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Организация не найдена."


async def test_patch_organization_invalid_id(
    authorized_client: AsyncClient,
) -> None:
    """Reject an organization ID that is not a UUID.

    Отклонить идентификатор организации, не являющийся UUID.
    """
    response = await authorized_client.patch(
        f"{URL}/not-a-uuid",
        json={"name": "ООО Новое название"},
    )

    assert response.status_code == 422


async def test_patch_foreign_organization_forbidden(
    authorized_client: AsyncClient,
    user: User,
    users: list[User],
    make_organization: Any,
    db_session: AsyncSession,
) -> None:
    """Reject an update to an organization owned by another user.

    Отклонить изменение организации, принадлежащей другому пользователю.
    """
    foreign_organization = await make_organization(
        owner=users[0],
        name="Чужая организация",
        inn="345678901234",
        address="г. Москва",
    )

    original_name = foreign_organization.name
    original_inn = foreign_organization.inn
    original_address = foreign_organization.address

    assert foreign_organization.owner_id != user.id

    response = await authorized_client.patch(
        f"{URL}/{foreign_organization.id}",
        json={"name": "Попытка изменения"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("Организация принадлежит другому пользователю.")

    await db_session.refresh(foreign_organization)

    assert foreign_organization.name == original_name
    assert foreign_organization.inn == original_inn
    assert foreign_organization.address == original_address


async def test_patch_organization_without_cookie(
    client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject a request without a session cookie.

    Отклонить запрос без cookie сессии.
    """
    original_name = organization.name

    response = await client.patch(
        f"{URL}/{organization.id}",
        json={"name": "Попытка изменения"},
    )

    assert response.status_code == 401

    await db_session.refresh(organization)
    assert organization.name == original_name


async def test_patch_organization_invalid_cookie(
    client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject a request with an invalid session cookie.

    Отклонить запрос с невалидной cookie сессии.
    """
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")
    original_name = organization.name

    response = await client.patch(
        f"{URL}/{organization.id}",
        json={"name": "Попытка изменения"},
    )

    assert response.status_code == 401

    await db_session.refresh(organization)
    assert organization.name == original_name


async def test_patch_organization_inactive_user(
    client: AsyncClient,
    session_for_inactive_user: dict[str, Any],
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject a request from an inactive user.

    Отклонить запрос неактивного пользователя.
    """
    client.cookies.set(
        SESSION_COOKIE_NAME,
        session_for_inactive_user["token"],
    )
    original_name = organization.name

    response = await client.patch(
        f"{URL}/{organization.id}",
        json={"name": "Попытка изменения"},
    )

    assert response.status_code == 401

    await db_session.refresh(organization)
    assert organization.name == original_name


async def test_patch_organization_empty_address_clears_value(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """An empty string replaces the address with an empty string.

    Пустая строка заменяет адрес на пустую строку.
    """
    original_address = organization.address
    assert original_address != ""  # убедимся, что фикстура даёт непустой адрес

    response = await authorized_client.patch(
        f"{URL}/{organization.id}",
        json={"address": ""},
    )

    assert response.status_code == 200
    assert response.json()["address"] == ""

    await db_session.refresh(organization)
    assert organization.address == ""
