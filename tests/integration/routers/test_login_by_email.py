"""
Integration tests for POST /auth/login/email.
"""

from httpx import AsyncClient

from app.models.system import User
from tests.fixtures.users import TEST_PASSWORD

SESSION_COOKIE_NAME = "session_id"


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
