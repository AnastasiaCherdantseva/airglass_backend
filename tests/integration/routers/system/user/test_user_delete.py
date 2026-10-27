"""Integration tests for deleting users through the HTTP API.

Интеграционные тесты удаления пользователей через HTTP API.
"""

from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime
from typing import TypeAlias
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    SESSION_COOKIE_NAME,
    SESSION_TTL,
    generate_session_token,
    hash_session_token,
)
from app.models.system import (
    ConditionType,
    Organization,
    Permission,
    PermissionAction,
    PermissionCondition,
    PermissionResource,
    PermissionZone,
    Role,
    Session,
    User,
    UserDirectPermission,
    UserOrganization,
    UserPermission,
    UserRole,
)

URL = "/api/users"

GrantPermission: TypeAlias = Callable[[], Awaitable[None]]
UserState: TypeAlias = tuple[datetime | None, bool] | None
DatabaseSnapshot: TypeAlias = tuple[tuple[int, ...], UserState]


@pytest.fixture
async def grant_users_delete(
    db_session: AsyncSession,
    user: User,
    make_permission,
    make_condition,
    make_user_permission,
) -> AsyncIterator[GrantPermission]:
    """Grant USERS.DELETE directly to the authenticated actor.

    Выдать право USERS.DELETE непосредственно авторизованному актору.
    """

    async def grant() -> None:
        permission = await db_session.scalar(
            select(Permission).where(
                Permission.resource == PermissionResource.USERS,
                Permission.action == PermissionAction.DELETE,
            )
        )

        if permission is None:
            permission = await make_permission(
                resource=PermissionResource.USERS,
                action=PermissionAction.DELETE,
                zone=PermissionZone.PUBLIC,
            )

        condition = await make_condition(
            permission=permission,
            type_=ConditionType.SUBTREE,
            is_active=True,
        )

        await make_user_permission(user=user, condition=condition)
        await db_session.flush()

    yield grant


async def _database_snapshot(
    db_session: AsyncSession,
    target_id: UUID,
) -> DatabaseSnapshot:
    """Capture database counts and the target's deletion state.

    Сохранить количество записей и состояние удаления целевого пользователя.
    """
    models = (
        User,
        UserRole,
        UserOrganization,
        UserDirectPermission,
        UserPermission,
        Session,
        Role,
        Organization,
    )

    counts: list[int] = []

    for model in models:
        count = await db_session.scalar(select(func.count()).select_from(model))
        counts.append(count or 0)

    row = (
        await db_session.execute(
            select(User.deleted_at, User.is_active).where(User.id == target_id)
        )
    ).one_or_none()

    state: UserState = None if row is None else (row[0], row[1])

    return tuple(counts), state


async def _count_links_for_users(
    db_session: AsyncSession,
    model: type,
    user_ids: list[UUID],
) -> int:
    """Count user-dependent rows for the specified users.

    Подсчитать зависимые записи для указанных пользователей.
    """
    user_id_column = model.user_id
    result = await db_session.scalar(
        select(func.count()).select_from(model).where(user_id_column.in_(user_ids))
    )
    return result or 0


async def _make_session(
    db_session: AsyncSession,
    user_id: UUID,
) -> Session:
    """Create a valid session for a user.

    Создать действующую сессию пользователя.
    """
    token = generate_session_token()
    now = datetime.now(UTC)

    session = Session(
        user_id=user_id,
        token_hash=hash_session_token(token),
        expires_at=now + SESSION_TTL,
        last_used_at=now,
    )
    db_session.add(session)
    await db_session.flush()

    return session


async def test_delete_user_deletes_subtree_and_dependent_data(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    make_user,
    make_role,
    make_organization: Callable[..., Awaitable[Organization]],
    make_user_role,
    make_user_organization,
    make_user_permission,
    make_user_direct_permission,
    grant_users_delete: GrantPermission,
) -> None:
    """Delete a child, its descendants, and dependent data.

    Удалить ребёнка, его потомков и зависимые данные.
    """
    await grant_users_delete()

    target = await make_user(
        email="delete.target@example.com",
        parent_id=user.id,
    )
    grandchild = await make_user(
        email="delete.grandchild@example.com",
        parent_id=target.id,
    )

    target_role = await make_role(name="some_role1", owner_id=target.id)
    grandchild_role = await make_role(name="some_role2", owner_id=grandchild.id)
    outside_role = await make_role(name="some_role3", owner_id=user.id)

    target_org = await make_organization(owner=target)
    grandchild_org = await make_organization(owner=grandchild)
    outside_org = await make_organization(owner=user)

    await make_user_role(target, target_role)
    await make_user_role(grandchild, grandchild_role)
    await make_user_organization(target, target_org)
    await make_user_organization(grandchild, grandchild_org)

    permission = await db_session.scalar(
        select(Permission).where(
            Permission.resource == PermissionResource.USERS,
            Permission.action == PermissionAction.DELETE,
        )
    )
    assert permission is not None

    condition = await db_session.scalar(
        select(PermissionCondition).where(
            PermissionCondition.permission_id == permission.id,
            PermissionCondition.is_active.is_(True),
        )
    )
    assert condition is not None

    await make_user_permission(user=target, condition=condition)
    await make_user_permission(user=grandchild, condition=condition)
    await make_user_direct_permission(user=target, condition=condition)
    await make_user_direct_permission(user=grandchild, condition=condition)

    await _make_session(db_session, target.id)
    await _make_session(db_session, grandchild.id)
    await db_session.flush()

    target_id = target.id
    grandchild_id = grandchild.id
    target_role_id = target_role.id
    grandchild_role_id = grandchild_role.id
    outside_role_id = outside_role.id
    target_org_id = target_org.id
    grandchild_org_id = grandchild_org.id
    outside_org_id = outside_org.id

    response = await authorized_client.delete(f"{URL}/{target_id}")

    assert response.status_code == 204
    assert response.content == b""

    for user_id in (target_id, grandchild_id):
        state = (
            await db_session.execute(
                select(User.deleted_at, User.is_active).where(User.id == user_id)
            )
        ).one()

        assert state.deleted_at is not None
        assert state.is_active is False

    subtree_ids = [target_id, grandchild_id]

    for model in (
        UserRole,
        UserOrganization,
        UserDirectPermission,
        UserPermission,
        Session,
    ):
        assert (
            await _count_links_for_users(
                db_session,
                model,
                subtree_ids,
            )
            == 0
        )

    for role_id in (target_role_id, grandchild_role_id):
        assert await db_session.scalar(select(Role.id).where(Role.id == role_id)) is None

    for organization_id in (target_org_id, grandchild_org_id):
        assert (
            await db_session.scalar(
                select(Organization.id).where(Organization.id == organization_id)
            )
            is None
        )

    assert (
        await db_session.scalar(select(Role.id).where(Role.id == outside_role_id))
        == outside_role_id
    )

    assert (
        await db_session.scalar(select(Organization.id).where(Organization.id == outside_org_id))
        == outside_org_id
    )


async def test_delete_user_grandchild(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    make_user,
    grant_users_delete: GrantPermission,
) -> None:
    """Delete a grandchild without deleting its parent.

    Удалить внука, не удаляя его родителя.
    """
    await grant_users_delete()

    parent = await make_user(
        email="delete.parent@example.com",
        parent_id=user.id,
    )
    target = await make_user(
        email="delete.deep.target@example.com",
        parent_id=parent.id,
    )
    target_id = target.id
    parent_id = parent.id

    response = await authorized_client.delete(f"{URL}/{target_id}")

    assert response.status_code == 204
    assert response.content == b""

    target_state = (
        await db_session.execute(
            select(User.deleted_at, User.is_active).where(User.id == target_id)
        )
    ).one()
    assert target_state.deleted_at is not None
    assert target_state.is_active is False

    parent_state = (
        await db_session.execute(
            select(User.deleted_at, User.is_active).where(User.id == parent_id)
        )
    ).one()
    assert parent_state.deleted_at is None
    assert parent_state.is_active is True


async def test_delete_user_without_cookie(
    client: AsyncClient,
    user: User,
    make_user,
    db_session: AsyncSession,
) -> None:
    """Reject deletion without an authentication cookie.

    Отклонить удаление без cookie аутентификации.
    """
    target = await make_user(
        email="delete.no-cookie@example.com",
        parent_id=user.id,
    )
    before = await _database_snapshot(db_session, target.id)

    response = await client.delete(f"{URL}/{target.id}")

    assert response.status_code == 401
    assert await _database_snapshot(db_session, target.id) == before


async def test_delete_user_with_invalid_cookie(
    client: AsyncClient,
    user: User,
    make_user,
    db_session: AsyncSession,
) -> None:
    """Reject deletion with an invalid authentication cookie.

    Отклонить удаление с невалидной cookie аутентификации.
    """
    target = await make_user(
        email="delete.invalid-cookie@example.com",
        parent_id=user.id,
    )
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")
    before = await _database_snapshot(db_session, target.id)

    response = await client.delete(f"{URL}/{target.id}")

    assert response.status_code == 401
    assert await _database_snapshot(db_session, target.id) == before


async def test_delete_user_with_inactive_actor(
    client: AsyncClient,
    session_for_inactive_user: dict,
    user: User,
    make_user,
    db_session: AsyncSession,
) -> None:
    """Reject deletion by an inactive authenticated user.

    Отклонить удаление от имени неактивного пользователя.
    """
    target = await make_user(
        email="delete.inactive-actor@example.com",
        parent_id=user.id,
    )
    client.cookies.set(
        SESSION_COOKIE_NAME,
        session_for_inactive_user["token"],
    )
    before = await _database_snapshot(db_session, target.id)

    response = await client.delete(f"{URL}/{target.id}")

    assert response.status_code == 401
    assert await _database_snapshot(db_session, target.id) == before


async def test_delete_user_without_permission(
    authorized_client: AsyncClient,
    user: User,
    make_user,
    db_session: AsyncSession,
) -> None:
    """Reject deletion when the actor lacks USERS.DELETE.

    Отклонить удаление, если у актора нет права USERS.DELETE.
    """
    target = await make_user(
        email="delete.no-permission@example.com",
        parent_id=user.id,
    )
    before = await _database_snapshot(db_session, target.id)

    response = await authorized_client.delete(f"{URL}/{target.id}")

    assert response.status_code == 403
    assert await _database_snapshot(db_session, target.id) == before


async def test_delete_user_outside_actor_subtree(
    authorized_client: AsyncClient,
    user: User,
    make_user,
    db_session: AsyncSession,
    grant_users_delete: GrantPermission,
) -> None:
    """Reject deletion of a user outside the actor's subtree.

    Отклонить удаление пользователя вне поддерева актора.
    """
    await grant_users_delete()

    target = await make_user(
        email="delete.outside-subtree@example.com",
    )
    before = await _database_snapshot(db_session, target.id)

    response = await authorized_client.delete(f"{URL}/{target.id}")

    assert response.status_code == 403
    assert await _database_snapshot(db_session, target.id) == before


async def test_delete_user_not_found(
    authorized_client: AsyncClient,
    db_session: AsyncSession,
    grant_users_delete: GrantPermission,
) -> None:
    """Return 404 when the target user does not exist.

    Вернуть 404, если целевой пользователь не существует.
    """
    await grant_users_delete()

    missing_id = uuid4()
    before = await _database_snapshot(db_session, missing_id)

    response = await authorized_client.delete(f"{URL}/{missing_id}")

    assert response.status_code == 404
    assert await _database_snapshot(db_session, missing_id) == before


async def test_delete_user_self_deletion_is_rejected(
    authorized_client: AsyncClient,
    user: User,
    db_session: AsyncSession,
    grant_users_delete: GrantPermission,
) -> None:
    """Reject an attempt to delete the actor.

    Отклонить попытку удалить самого актора.
    """
    await grant_users_delete()
    before = await _database_snapshot(db_session, user.id)

    response = await authorized_client.delete(f"{URL}/{user.id}")

    assert response.status_code == 422
    assert await _database_snapshot(db_session, user.id) == before


async def test_delete_user_invalid_uuid(
    authorized_client: AsyncClient,
    grant_users_delete,
) -> None:
    """Reject a path parameter that is not a UUID.

    Отклонить параметр пути, который не является UUID.
    """
    await grant_users_delete()

    response = await authorized_client.delete(f"{URL}/not-a-uuid")

    assert response.status_code == 422
