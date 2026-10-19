"""Integration tests for user creation endpoint.

Интеграционные тесты эндпоинта создания пользователя.
"""

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import is_verified_password
from app.models.system import (
    Permission,
    PermissionAction,
    PermissionCondition,
    PermissionEffect,
    PermissionResource,
    PermissionZone,
    User,
    UserOrganization,
)
from app.models.system.permission_condition import ConditionType
from app.models.system.role import Role


@pytest.fixture
def valid_user_payload(role: Any) -> dict[str, Any]:
    """Return a valid user creation payload.

    Возвращает корректные данные для создания пользователя.
    """
    return {
        "email": "new.user@example.com",
        "name": "New User",
        "password": "StrongPassword123!",
        "role_ids": [str(role.id)],
    }


@pytest.fixture
async def grant_users_create(
    db_session: AsyncSession, user: User, make_permission, make_condition, make_user_permission
) -> AsyncIterator[Callable[[Any], Awaitable[None]]]:
    """Grant the authenticated actor permission to create users.

    Выдаёт авторизованному пользователю право создавать пользователей.
    """

    async def grant(role: Any) -> None:
        permission = await db_session.scalar(
            select(Permission).where(
                Permission.resource == PermissionResource.USERS,
                Permission.action == PermissionAction.CREATE,
            )
        )

        if permission is None:
            permission = await make_permission(
                resource=PermissionResource.USERS,
                action=PermissionAction.CREATE,
                zone=PermissionZone.PUBLIC,
            )
        condition = await db_session.scalar(
            select(PermissionCondition).where(
                PermissionCondition.permission_id == permission.id,
                PermissionCondition.type == ConditionType.ROLE,
                PermissionCondition.role_id == role.id,
                PermissionCondition.effect == PermissionEffect.ALLOW,
                PermissionCondition.is_active.is_(True),
            )
        )

        if condition is None:
            condition = await make_condition(
                permission=permission,
                type_=ConditionType.ROLE,
                role_id=role.id,
                effect=PermissionEffect.ALLOW,
                is_active=True,
            )

        await db_session.flush()

        await make_user_permission(
            user=user,
            condition=condition,
        )

        await db_session.flush()

    yield grant


async def count_users(db_session: AsyncSession) -> int:
    """Return the number of users in the current transaction.

    Возвращает количество пользователей в текущей транзакции.
    """
    result = await db_session.scalar(select(func.count()).select_from(User))
    return result or 0


async def count_user_organization_links(
    db_session: AsyncSession,
    user_id: UUID,
) -> int:
    """Count organization links for a user.

    Считает связи пользователя с организациями.
    """
    result = await db_session.scalar(
        select(func.count())
        .select_from(UserOrganization)
        .where(UserOrganization.user_id == user_id)
    )
    return result or 0


@pytest.mark.asyncio
async def test_create_user_returns_201_and_hashes_password(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Create a user and verify the stored password hash.

    Создаёт пользователя и проверяет сохранённый хеш пароля.
    """
    await grant_users_create(role)

    response = await authorized_client.post(
        "/api/users",
        json=valid_user_payload,
    )

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == valid_user_payload["email"]
    assert body["name"] == valid_user_payload["name"]
    assert body["is_active"] is False
    assert body["parent_id"] == str(user.id)
    assert body["role_ids"] == [str(role.id)]

    stored_user = await db_session.scalar(
        select(User).where(User.email == valid_user_payload["email"])
    )

    assert stored_user is not None
    assert stored_user.password_hash != valid_user_payload["password"]
    assert is_verified_password(
        valid_user_payload["password"],
        stored_user.password_hash,
    )


@pytest.mark.asyncio
async def test_create_user_without_organization_ids(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Create a user when organization_ids is omitted.

    Создаёт пользователя, если organization_ids не передан.
    """
    await grant_users_create(role)

    response = await authorized_client.post(
        "/api/users",
        json=valid_user_payload,
    )

    assert response.status_code == 201

    created_user = await db_session.scalar(
        select(User).where(User.email == valid_user_payload["email"])
    )

    assert created_user is not None
    assert (
        await count_user_organization_links(
            db_session,
            created_user.id,
        )
        == 0
    )


@pytest.mark.asyncio
async def test_create_user_with_empty_organization_ids(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Create a user with an empty organization_ids list.

    Создаёт пользователя с пустым списком organization_ids.
    """
    await grant_users_create(role)
    payload = {**valid_user_payload, "organization_ids": []}

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 201

    created_user = await db_session.scalar(select(User).where(User.email == payload["email"]))

    assert created_user is not None
    assert (
        await count_user_organization_links(
            db_session,
            created_user.id,
        )
        == 0
    )


@pytest.mark.asyncio
async def test_create_user_links_owned_organizations(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
    make_organization,
) -> None:
    """Link the created user to organizations owned by the actor.

    Связывает созданного пользователя с организациями владельца.
    """
    await grant_users_create(role)

    first_org = await make_organization(owner=user)
    second_org = await make_organization(owner=user)
    await db_session.flush()

    payload = {
        **valid_user_payload,
        "organization_ids": [str(first_org.id), str(second_org.id)],
    }

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 201

    created_user = await db_session.scalar(select(User).where(User.email == payload["email"]))
    assert created_user is not None

    linked_ids = set(
        (
            await db_session.scalars(
                select(UserOrganization.organization_id).where(
                    UserOrganization.user_id == created_user.id
                )
            )
        ).all()
    )

    assert linked_ids == {first_org.id, second_org.id}


@pytest.mark.asyncio
async def test_create_user_without_permission_returns_403(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    valid_user_payload: dict[str, Any],
) -> None:
    """Reject user creation when the actor lacks permission.

    Запрещает создание пользователя без соответствующего права.
    """
    users_before = await count_users(db_session)

    response = await authorized_client.post(
        "/api/users",
        json=valid_user_payload,
    )

    assert response.status_code == 403
    assert await count_users(db_session) == users_before


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email_returns_409(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
    make_user,
) -> None:
    """Reject user creation when the email already exists.

    Запрещает создание пользователя с уже существующим email.
    """
    await grant_users_create(role)
    await make_user(email=valid_user_payload["email"])
    await db_session.flush()

    users_before = await count_users(db_session)

    response = await authorized_client.post(
        "/api/users",
        json=valid_user_payload,
    )

    assert response.status_code == 409
    assert await count_users(db_session) == users_before


@pytest.mark.asyncio
async def test_create_user_with_unknown_role_returns_404(
    authorized_client: AsyncClient,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Reject user creation when a requested role does not exist.

    Запрещает создание пользователя с несуществующей ролью.
    """
    await grant_users_create(role)
    payload = {**valid_user_payload, "role_ids": [str(uuid4())]}

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_with_inactive_role_returns_422(
    authorized_client: AsyncClient,
    role: Any,
    inactive_role: Role,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Reject user creation with an inactive role.

    Запрещает создание пользователя с неактивной ролью.
    """
    await grant_users_create(role)
    payload = {
        **valid_user_payload,
        "role_ids": [str(inactive_role.id)],
    }

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_with_disallowed_role_returns_403(
    authorized_client: AsyncClient,
    role: Any,
    system_role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Reject a role that the actor is not allowed to assign.

    Запрещает назначение роли, которую актор не вправе выдавать.
    """
    await grant_users_create(role)
    payload = {
        **valid_user_payload,
        "role_ids": [str(system_role.id)],
    }

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_with_unknown_organization_returns_404(
    authorized_client: AsyncClient,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Reject an organization ID that does not exist.

    Запрещает передачу идентификатора несуществующей организации.
    """
    await grant_users_create(role)
    payload = {
        **valid_user_payload,
        "organization_ids": [str(UUID(int=0))],
    }

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_with_foreign_organization_returns_403(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    role: Any,
    valid_user_payload: dict[str, Any],
    make_user: Callable[..., Awaitable[User]],
    grant_users_create: Callable[[Any], Awaitable[None]],
    make_organization,
) -> None:
    """Reject an organization owned by another user.

    Запрещает передачу организации, принадлежащей другому пользователю.
    """
    await grant_users_create(role)

    foreign_owner = await make_user(email="foreign.owner@example.com")
    organization = await make_organization(owner=foreign_owner)
    await db_session.flush()

    payload = {
        **valid_user_payload,
        "organization_ids": [str(organization.id)],
    }

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_with_invalid_name_returns_422(
    authorized_client: AsyncClient,
    role: Any,
    valid_user_payload: dict[str, Any],
    grant_users_create: Callable[[Any], Awaitable[None]],
) -> None:
    """Reject a user payload with an invalid name.

    Отклоняет данные пользователя с некорректным именем.
    """
    await grant_users_create(role)
    payload = {**valid_user_payload, "name": ""}

    response = await authorized_client.post("/api/users", json=payload)

    assert response.status_code == 422
