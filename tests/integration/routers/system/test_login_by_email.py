"""
Integration tests for POST /auth/login/email.
"""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME
from app.models.system import User
from app.models.system.session import Session
from tests.fixtures.users import TEST_PASSWORD


async def test_login_success(
    client: AsyncClient,
    user: User,
    db_session,
) -> None:
    """Успешный логин: 200, cookie установлен, токена нет в body."""
    response = await client.post(
        "/api/auth/login/email",
        json={
            "email": user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == user.email
    assert body["name"] == user.name
    # session_token НЕ должен быть в body
    assert "session_token" not in body

    # Cookie установлен
    assert SESSION_COOKIE_NAME in response.cookies


async def test_login_wrong_password(
    client: AsyncClient,
    user: User,
) -> None:
    """Неверный пароль → 401."""
    response = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": "wrongsecretsecretsecret"},
    )

    assert response.status_code == 401


async def test_login_user_not_found(
    client: AsyncClient,
) -> None:
    """Юзер не найден → 401."""
    response = await client.post(
        "/api/auth/login/email",
        json={"email": "unknown@example.com", "password": TEST_PASSWORD},
    )

    assert response.status_code == 401


async def test_login_inactive_user(
    client: AsyncClient,
    inactive_user: User,
) -> None:
    """Неактивный юзер → 401."""
    response = await client.post(
        "/api/auth/login/email",
        json={"email": inactive_user.email, "password": TEST_PASSWORD},
    )

    assert response.status_code == 401


async def test_login_invalid_payload(
    client: AsyncClient,
) -> None:
    """Невалидные данные → 422."""
    response = await client.post(
        "/api/auth/login/email",
        json={"email": "not-an-email", "password": "x"},
    )

    assert response.status_code == 422


async def test_login_when_already_authenticated(
    client: AsyncClient,
    user: User,
) -> None:
    """Логин при активной сессии → 409."""
    first = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert second.status_code == 409


async def test_login_when_session_expired(
    client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Cookie есть, но сессия мертва → логин как обычно."""
    first = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert first.status_code == 200

    # Убиваем сессию
    session = (await db_session.execute(select(Session))).scalar_one()
    session.expires_at = datetime.now(UTC) - timedelta(days=1)
    await db_session.flush()

    second = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert second.status_code == 200
