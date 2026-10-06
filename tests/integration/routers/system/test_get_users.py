"""
Integration tests for GET /users.

Интеграционные тесты GET /users.
"""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient

from app.models.system import (
    ConditionType,
    Permission,
    PermissionAction,
    PermissionCondition,
    PermissionResource,
    Role,
    User,
    UserRole,
)

URL = "/api/users"

ITEM_KEYS = {"id", "email", "name", "is_active", "parent_id", "role_ids", "children_count"}

MakeUser = Callable[..., Awaitable[User]]
MakeUserRole = Callable[[User, Role], Awaitable[UserRole]]
MakeCondition = Callable[..., Awaitable[PermissionCondition]]


def _ids(body: dict[str, Any]) -> list[str]:
    """Ids of items in the response, in order. / Id элементов ответа по порядку."""
    return [item["id"] for item in body["items"]]


# ─────────────────────────────────────────────────────────────
# 200 — результаты
# ─────────────────────────────────────────────────────────────


async def test_get_users_empty(authorized_client: AsyncClient, user_admin: User) -> None:
    """Нет детей → пустой список, limit/page из запроса."""
    response = await authorized_client.get(URL, params={"limit": 7, "page": 3})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 7, "page": 3}


async def test_get_users_one_child(
    authorized_client: AsyncClient,
    user_admin: User,
    make_user: MakeUser,
) -> None:
    """Один прямой ребёнок → один элемент, total=1."""
    child = await make_user(email="child@example.com", parent_id=user_admin.id)

    response = await authorized_client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert _ids(body) == [str(child.id)]
    assert body["total"] == 1


@pytest.mark.parametrize(
    ("page", "start"),
    [
        pytest.param(0, 0, id="first_page"),
        pytest.param(1, 2, id="second_page"),
        pytest.param(2, 4, id="last_partial_page"),
    ],
)
async def test_get_users_pagination(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
    page: int,
    start: int,
) -> None:
    """Пять детей, limit=2 → нужный срез в порядке created_at, total=5."""
    response = await authorized_client.get(URL, params={"limit": 2, "page": page})

    assert response.status_code == 200
    body = response.json()
    assert _ids(body) == [str(c.id) for c in children_user_admin[start : start + 2]]
    assert body["total"] == 5
    assert (body["limit"], body["page"]) == (2, page)


async def test_get_users_page_out_of_range(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
) -> None:
    """Страница за пределами → items=[], total реальный."""
    response = await authorized_client.get(URL, params={"limit": 2, "page": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 5


async def test_get_users_only_direct_children(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
    make_user: MakeUser,
) -> None:
    """Внуки не попадают в список актора."""
    grandchild = await make_user(
        email="grandchild@example.com", parent_id=children_user_admin[0].id
    )

    response = await authorized_client.get(URL)

    body = response.json()
    assert set(_ids(body)) == {str(c.id) for c in children_user_admin}
    assert str(grandchild.id) not in _ids(body)
    assert body["total"] == 5


async def test_get_users_soft_deleted_excluded(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
    make_user: MakeUser,
) -> None:
    """Мягко удалённый ребёнок не попадает ни в items, ни в total."""
    deleted = await make_user(
        email="deleted@example.com",
        parent_id=user_admin.id,
        deleted_at=datetime.now(UTC),
    )

    response = await authorized_client.get(URL)

    body = response.json()
    assert str(deleted.id) not in _ids(body)
    assert body["total"] == 5


# ─────────────────────────────────────────────────────────────
# 200 — роли и форма ответа
# ─────────────────────────────────────────────────────────────


async def test_get_users_roles_in_response(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
    role: Role,
    system_role: Role,
    make_user_role: MakeUserRole,
) -> None:
    """Роли ребёнка попадают в role_ids."""
    child = children_user_admin[0]
    await make_user_role(child, role)
    await make_user_role(child, system_role)

    response = await authorized_client.get(URL)

    item = next(i for i in response.json()["items"] if i["id"] == str(child.id))
    assert set(item["role_ids"]) == {str(role.id), str(system_role.id)}


async def test_get_users_child_without_roles(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
) -> None:
    """Дети без ролей → role_ids=[]."""
    response = await authorized_client.get(URL)

    assert response.status_code == 200
    assert all(item["role_ids"] == [] for item in response.json()["items"])


async def test_get_users_item_fields(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
    role: Role,
    make_user: MakeUser,
    make_user_role: MakeUserRole,
) -> None:
    """Все поля meUsersListItem заполнены корректно."""
    child = children_user_admin[0]
    await make_user(email="grandchild@example.com", parent_id=child.id)
    await make_user_role(child, role)

    response = await authorized_client.get(URL)

    item = next(i for i in response.json()["items"] if i["id"] == str(child.id))
    assert set(item) == ITEM_KEYS
    assert item == {
        "id": str(child.id),
        "email": child.email,
        "name": child.name,
        "is_active": child.is_active,
        "parent_id": str(user_admin.id),
        "role_ids": [str(role.id)],
        "children_count": 1,
    }


async def test_get_users_wrapper_and_defaults(
    authorized_client: AsyncClient,
    user_admin: User,
    children_user_admin: list[User],
) -> None:
    """В корне ровно {items, total, limit, page}; дефолты limit=50, page=0."""
    response = await authorized_client.get(URL)

    body = response.json()
    assert set(body) == {"items", "total", "limit", "page"}
    assert (body["limit"], body["page"]) == (50, 0)


@pytest.mark.parametrize("limit", [1, 100])
async def test_get_users_limit_boundaries(
    authorized_client: AsyncClient,
    user_admin: User,
    limit: int,
) -> None:
    """Границы limit (1 и 100) допустимы."""
    response = await authorized_client.get(URL, params={"limit": limit})

    assert response.status_code == 200
    assert response.json()["limit"] == limit


# ─────────────────────────────────────────────────────────────
# 401 / 403 / 422
# ─────────────────────────────────────────────────────────────


async def test_get_users_not_authenticated(client: AsyncClient) -> None:
    """Без cookie → 401."""
    response = await client.get(URL)

    assert response.status_code == 401


async def test_get_users_without_permission(authorized_client: AsyncClient) -> None:
    """Актор без прав → 403."""
    response = await authorized_client.get(URL)

    assert response.status_code == 403


async def test_get_users_other_permission_only(
    authorized_client: AsyncClient,
    user: User,
    permissions: list[Permission],
    make_condition: MakeCondition,
    make_user_permission: Callable[..., Awaitable[Any]],
) -> None:
    """Есть другое право (USERS.CREATE), но нет USERS.READ → 403."""
    target = next(
        p
        for p in permissions
        if p.resource == PermissionResource.USERS and p.action == PermissionAction.CREATE
    )
    condition = await make_condition(target, type_=ConditionType.ALL)
    await make_user_permission(user, condition)

    response = await authorized_client.get(URL)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"limit": 0}, id="limit_zero"),
        pytest.param({"limit": 101}, id="limit_over_max"),
        pytest.param({"page": -1}, id="page_negative"),
        pytest.param({"limit": "abc"}, id="limit_not_int"),
    ],
)
async def test_get_users_invalid_query(
    authorized_client: AsyncClient,
    user_admin: User,
    params: dict[str, Any],
) -> None:
    """Невалидные query-параметры → 422 (актор авторизован и имеет право)."""
    response = await authorized_client.get(URL, params=params)

    assert response.status_code == 422
