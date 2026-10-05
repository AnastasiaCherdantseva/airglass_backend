"""Tests for get_current_user dependency."""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME, SESSION_TTL
from app.models.system import (
    User,
)
from app.models.system.permission import Permission
from app.models.system.user_permission import UserPermission

# ─────────────────────────────────────────────────────────────
# 401 — неаутентифицирован
# ─────────────────────────────────────────────────────────────


async def test_no_cookie(client: AsyncClient) -> None:
    """Без cookie — 401."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_invalid_cookie(client: AsyncClient) -> None:
    """Невалидный токен — 401."""
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_expired_session(
    client: AsyncClient,
    user: User,
    session: dict,
    db_session: AsyncSession,
) -> None:
    """Истёкшая сессия — 401."""
    session_obj = session["data"]
    session_obj.expires_at = datetime.now(UTC) - timedelta(days=1)
    await db_session.flush()
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_inactive_user(
    client: AsyncClient,
    session_for_inactive_user: dict,
    db_session: AsyncSession,
) -> None:
    """Неактивный юзер — 401."""
    token = session_for_inactive_user["token"]
    client.cookies.set(SESSION_COOKIE_NAME, token)
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_unverified_user(
    client: AsyncClient,
    user: User,
    session: dict,
    db_session: AsyncSession,
) -> None:
    """Юзер без email_verified — 401."""
    user.email_verified = None
    await db_session.flush()
    token = session["token"]
    client.cookies.set(SESSION_COOKIE_NAME, token)
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_deleted_user(
    client: AsyncClient,
    user: User,
    session: dict,
    db_session: AsyncSession,
) -> None:
    """Удалённый юзер — 401."""
    user.deleted_at = datetime.now(UTC)
    await db_session.flush()
    token = session["token"]
    client.cookies.set(SESSION_COOKIE_NAME, token)
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


# ─────────────────────────────────────────────────────────────
# 200 — успех
# ─────────────────────────────────────────────────────────────


async def test_success_returns_user_data(
    client: AsyncClient, user: User, session: dict, user_permissions: list[UserPermission]
) -> None:
    """Успех — 200, возвращает данные юзера."""
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["is_active"] == user.is_active

    conditions = []
    for p in body["permissions"]:
        conditions.extend(p["conditions"])

    assert {d["id"] for d in conditions} == {str(d.condition_id) for d in user_permissions}
    assert body["has_admin_access"] is True


async def test_success_empty_permissions(
    client: AsyncClient,
    user: User,
    session: dict,
) -> None:
    """Успех — пустой список прав, если user_permissions пустая."""
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["permissions"] == []
    assert body["has_admin_access"] is False


async def test_success_with_permissions(
    client: AsyncClient,
    user: User,
    session: dict,
    permissions: list[Permission],
    user_permissions: list[UserPermission],
) -> None:
    """Успех — права юзера возвращаются."""

    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert len(body["permissions"]) == 12
    for p in body["permissions"]:
        assert any(pp.code == p["code"] for pp in permissions)


async def test_success_has_admin_access(
    client: AsyncClient,
    user: User,
    session: dict,
    user_permissions: list[UserPermission],
) -> None:
    """Успех — has_admin_access=True, если есть admin-право."""
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["has_admin_access"] is True


# ─────────────────────────────────────────────────────────────
# Продление сессии
# ─────────────────────────────────────────────────────────────


async def test_session_extended(
    client: AsyncClient,
    user: User,
    session: dict,
    db_session: AsyncSession,
) -> None:
    """Сессия продлевается при запросе, если last_used_at старый."""
    session_obj = session["data"]
    old_time = datetime.now(UTC) - timedelta(hours=25)
    session_obj.last_used_at = old_time
    session_obj.expires_at = old_time + SESSION_TTL
    await db_session.flush()

    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200

    await db_session.refresh(session_obj)
    assert session_obj.last_used_at > old_time
    assert session_obj.expires_at > old_time + SESSION_TTL


async def test_session_not_extended_if_recent(
    client: AsyncClient,
    user: User,
    session: dict,
    db_session: AsyncSession,
) -> None:
    """Сессия НЕ продлевается, если last_used_at свежий."""
    session_obj = session["data"]
    original_last_used = session_obj.last_used_at
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    response = await client.get("/api/auth/me")
    assert response.status_code == 200

    await db_session.refresh(session_obj)
    assert session_obj.last_used_at == original_last_used
