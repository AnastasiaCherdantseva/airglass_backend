from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import Organization, User, UserOrganization

URL = "/api/organizations"


async def test_delete_organization_success(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Delete an owned organization and verify the database state.

    Удалить свою организацию и проверить состояние базы данных.
    """
    organization_id = organization.id

    response = await authorized_client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 204
    assert response.content == b""

    deleted_organization = await db_session.get(Organization, organization_id)
    assert deleted_organization is None


async def test_delete_organization_cascades_user_links(
    authorized_client: AsyncClient,
    user: User,
    organization: Organization,
    make_user_organization: Callable[[User, Organization], Awaitable[UserOrganization]],
    db_session: AsyncSession,
) -> None:
    """Delete user-organization links when the organization is deleted.

    Удалить связи пользователей с организацией при удалении организации.
    """
    await make_user_organization(user, organization)
    organization_id = organization.id

    response = await authorized_client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 204

    link = await db_session.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == organization_id,
        )
    )
    assert link is None

    deleted_organization = await db_session.get(Organization, organization_id)
    assert deleted_organization is None


async def test_deleted_organization_is_not_visible_in_get(
    authorized_client: AsyncClient,
    user: User,
    organization: Organization,
    make_user_organization: Callable[[User, Organization], Awaitable[UserOrganization]],
) -> None:
    """Ensure the deleted organization is absent from the user's list.

    Убедиться, что удалённая организация отсутствует в списке пользователя.
    """
    await make_user_organization(user, organization)
    organization_id = str(organization.id)

    delete_response = await authorized_client.delete(f"{URL}/{organization_id}")

    assert delete_response.status_code == 204

    get_response = await authorized_client.get(URL)

    assert get_response.status_code == 200
    assert all(item["id"] != organization_id for item in get_response.json())


async def test_delete_organization_not_found(
    authorized_client: AsyncClient,
) -> None:
    """Return 404 when the organization does not exist.

    Вернуть 404, если организация не существует.
    """
    response = await authorized_client.delete(f"{URL}/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Организация не найдена."


async def test_delete_organization_invalid_id(
    authorized_client: AsyncClient,
) -> None:
    """Reject an ID that is not a valid UUID.

    Отклонить идентификатор, не являющийся корректным UUID.
    """
    response = await authorized_client.delete(f"{URL}/not-a-uuid")

    assert response.status_code == 422


async def test_delete_foreign_organization_forbidden(
    authorized_client: AsyncClient,
    users: list[User],
    make_organization: Callable[..., Awaitable[Organization]],
    db_session: AsyncSession,
) -> None:
    """Reject deletion of an organization owned by another user.

    Отклонить удаление организации, принадлежащей другому пользователю.
    """
    foreign_organization = await make_organization(
        owner=users[0],
        address="г. Москва",
    )
    organization_id = foreign_organization.id
    original_name = foreign_organization.name

    response = await authorized_client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == ("Организация принадлежит другому пользователю.")

    existing_organization = await db_session.get(
        Organization,
        organization_id,
    )
    assert existing_organization is not None
    assert existing_organization.name == original_name


async def test_delete_organization_twice_returns_not_found(
    authorized_client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Return 404 when deleting the same organization a second time.

    Вернуть 404 при повторном удалении той же организации.
    """
    organization_id = organization.id

    first_response = await authorized_client.delete(f"{URL}/{organization_id}")
    assert first_response.status_code == 204
    assert first_response.content == b""

    second_response = await authorized_client.delete(f"{URL}/{organization_id}")
    assert second_response.status_code == 404
    assert second_response.json()["detail"] == "Организация не найдена."

    deleted_organization = await db_session.get(
        Organization,
        organization_id,
    )
    assert deleted_organization is None


async def test_delete_organization_without_cookie(
    client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject deletion without a session cookie.

    Отклонить удаление без cookie сессии.
    """
    organization_id = organization.id

    response = await client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 401

    existing_organization = await db_session.get(
        Organization,
        organization_id,
    )
    assert existing_organization is not None


async def test_delete_organization_invalid_cookie(
    client: AsyncClient,
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject deletion with an invalid session cookie.

    Отклонить удаление с невалидной cookie сессии.
    """
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")
    organization_id = organization.id

    response = await client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 401

    existing_organization = await db_session.get(
        Organization,
        organization_id,
    )
    assert existing_organization is not None


async def test_delete_organization_inactive_user(
    client: AsyncClient,
    session_for_inactive_user: dict[str, Any],
    organization: Organization,
    db_session: AsyncSession,
) -> None:
    """Reject deletion by an inactive user.

    Отклонить удаление от неактивного пользователя.
    """
    client.cookies.set(
        SESSION_COOKIE_NAME,
        session_for_inactive_user["token"],
    )
    organization_id = organization.id

    response = await client.delete(f"{URL}/{organization_id}")

    assert response.status_code == 401

    existing_organization = await db_session.get(
        Organization,
        organization_id,
    )
    assert existing_organization is not None
