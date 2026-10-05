from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient

from app.models.system import (
    Role,
    User,
)
from app.models.system.role_permission import RolePermission
from app.models.system.user_role import UserRole
from app.schemas.system.user import UserCreateRequest

URL = "/api/users"


async def test_create_user_success(
    authorized_client: AsyncClient,
    user_admin: User,
    role: Role,
    new_user_data_request: UserCreateRequest,
) -> None:
    """201, в ответе все поля; новый пользователь неактивен, parent_id = актор."""
    response = await authorized_client.post(URL, json=new_user_data_request)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "name", "is_active", "parent_id", "role_ids"}
    UUID(body["id"])
    assert body["email"] == "new@example.com"
    assert body["name"] == "Новый"
    assert body["is_active"] is False
    assert body["parent_id"] == str(user_admin.id)
    assert body["role_ids"] == [str(role.id)]
    assert "password" not in body


async def test_create_user_without_permission(
    authorized_client: AsyncClient,
    user_roles: list[UserRole],
    new_user_data_request: UserCreateRequest,
) -> None:
    """Нет USERS.CREATE → 403."""
    response = await authorized_client.post(URL, json=new_user_data_request)

    assert response.status_code == 403


async def test_create_user_foreign_role(
    authorized_client: AsyncClient,
    user_default_role: UserRole,
    role_permission: RolePermission,
    system_role: Role,
    new_user_data_request: UserCreateRequest,
) -> None:
    """Роль, на которую у актора нет ROLE-condition → 403."""
    payload = {**new_user_data_request, "role_ids": [str(system_role.id)]}

    response = await authorized_client.post(URL, json=payload)

    assert response.status_code == 403


async def test_create_user_email_taken(
    authorized_client: AsyncClient,
    user_admin: User,
    new_user_data_request: UserCreateRequest,
) -> None:
    """Email уже занят (регистр не важен) → 409."""
    payload = {**new_user_data_request, "email": user_admin.email.upper()}

    response = await authorized_client.post(URL, json=payload)

    assert response.status_code == 409


@pytest.mark.parametrize(
    "override",
    [
        pytest.param({"email": "not-an-email"}, id="invalid_email"),
        pytest.param({"password": "12345"}, id="short_password"),
        pytest.param({"role_ids": []}, id="empty_role_ids"),
    ],
)
async def test_create_user_invalid_payload(
    authorized_client: AsyncClient,
    user_admin: User,
    new_user_data_request: UserCreateRequest,
    override: dict[str, Any],
) -> None:
    """Невалидное тело → 422 (актор авторизован и имеет право)."""
    response = await authorized_client.post(URL, json={**new_user_data_request, **override})

    assert response.status_code == 422


async def test_create_user_not_authenticated(
    client: AsyncClient,
    user_admin: User,
    new_user_data_request: UserCreateRequest,
) -> None:
    """Без cookie → 401."""
    response = await client.post(URL, json=new_user_data_request)

    assert response.status_code == 401
