"""
Integration tests for POST /auth/logout.
"""

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import Session, User
from tests.fixtures.users import TEST_PASSWORD


async def test_logout_success(
    client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Логин → логаут: 204, cookie сброшен, сессии нет в БД."""
    # 1. Логинимся, чтобы получить cookie
    login_response = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert login_response.status_code == 200
    assert SESSION_COOKIE_NAME in login_response.cookies

    # Проверяем, что сессия создана
    sessions_before = (await db_session.execute(select(Session))).scalars().all()
    assert len(sessions_before) == 1

    # 2. Логаут
    logout_response = await client.post("/api/auth/logout")

    # 3. Проверки
    assert logout_response.status_code == 204

    # Сессия удалена из БД
    sessions_after = (await db_session.execute(select(Session))).scalars().all()
    assert sessions_after == []

    # Cookie сброшена (max_age=0 → значение пустое или отсутствует)
    assert logout_response.cookies.get(SESSION_COOKIE_NAME) in (None, "")


async def test_logout_without_cookie(client: AsyncClient) -> None:
    """Логаут без cookie → 204 (идемпотентно)."""
    response = await client.post("/api/auth/logout")

    assert response.status_code == 204


async def test_logout_with_invalid_cookie(client: AsyncClient) -> None:
    """Логаут с мусорным токеном → 204 (идемпотентно)."""
    client.cookies.set(SESSION_COOKIE_NAME, "invalid-token-that-does-not-exist")

    response = await client.post("/api/auth/logout")

    assert response.status_code == 204
    assert response.cookies.get(SESSION_COOKIE_NAME) in (None, "")


async def test_logout_twice(
    client: AsyncClient,
    user: User,
) -> None:
    """Двойной логаут → оба 204 (идемпотентность)."""
    # Логинимся
    await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )

    # Первый логаут
    first = await client.post("/api/auth/logout")
    assert first.status_code == 204

    assert first.cookies.get(SESSION_COOKIE_NAME) in (None, "")

    # Второй логаут — сессии уже нет
    second = await client.post("/api/auth/logout")
    assert second.status_code == 204

    assert second.cookies.get(SESSION_COOKIE_NAME) in (None, "")
