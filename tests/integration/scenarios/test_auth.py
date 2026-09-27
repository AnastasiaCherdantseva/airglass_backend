from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME, hash_session_token
from app.main import app
from app.models.system import Session, User
from tests.fixtures.users import TEST_PASSWORD


async def test_login_logout_login(
    client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """После логаута можно залогиниться снова и получить новую сессию."""
    # Первый логин
    first_login = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert first_login.status_code == 200
    first_token = first_login.cookies[SESSION_COOKIE_NAME]
    first_hash = hash_session_token(first_token)

    # Логаут
    logout = await client.post("/api/auth/logout")
    assert logout.status_code == 204

    # Старой сессии нет
    old_session = (
        await db_session.execute(select(Session).where(Session.token_hash == first_hash))
    ).scalar_one_or_none()
    assert old_session is None

    # Повторный логин
    second_login = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert second_login.status_code == 200
    second_token = second_login.cookies[SESSION_COOKIE_NAME]
    second_hash = hash_session_token(second_token)

    # Токены разные — новая сессия
    assert first_token != second_token
    assert first_hash != second_hash

    # В БД ровно одна сессия — новая
    sessions = (await db_session.execute(select(Session))).scalars().all()
    assert len(sessions) == 1
    assert sessions[0].token_hash == second_hash
    assert sessions[0].user_id == user.id


async def test_logout_removes_only_current_session(
    client: AsyncClient,
    user: User,
    db_session: AsyncSession,
) -> None:
    """Логаут удаляет только текущую сессию, не трогает другие."""
    # Первая сессия через client
    first_login = await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert first_login.status_code == 200
    first_token = first_login.cookies[SESSION_COOKIE_NAME]
    first_hash = hash_session_token(first_token)

    # Вторая сессия — через второй клиент (другой "браузер")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as second_client:
        second_login = await second_client.post(
            "/api/auth/login/email",
            json={"email": user.email, "password": TEST_PASSWORD},
        )
        assert second_login.status_code == 200
        second_token = second_login.cookies[SESSION_COOKIE_NAME]
        second_hash = hash_session_token(second_token)

        # В БД две сессии
        sessions = (await db_session.execute(select(Session))).scalars().all()
        assert len(sessions) == 2
        hashes = {s.token_hash for s in sessions}
        assert hashes == {first_hash, second_hash}

    # Логаут через первый клиент — удаляет только первую сессию
    logout = await client.post("/api/auth/logout")
    assert logout.status_code == 204

    # В БД осталась только вторая сессия
    sessions_after = (await db_session.execute(select(Session))).scalars().all()
    assert len(sessions_after) == 1
    assert sessions_after[0].token_hash == second_hash


async def test_logout_does_not_affect_other_users(
    client: AsyncClient,
    users: list[User],
    db_session: AsyncSession,
) -> None:
    """Логаут одного юзера не влияет на сессии других."""
    user_a, user_b = users[0], users[1]

    # Логин обоих через разные клиенты
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="https://test") as client_a:
        async with AsyncClient(transport=transport, base_url="https://test") as client_b:
            await client_a.post(
                "/api/auth/login/email",
                json={"email": user_a.email, "password": TEST_PASSWORD},
            )
            await client_b.post(
                "/api/auth/login/email",
                json={"email": user_b.email, "password": TEST_PASSWORD},
            )

            # В БД две сессии от разных юзеров
            sessions = (await db_session.execute(select(Session))).scalars().all()
            assert len(sessions) == 2
            assert {s.user_id for s in sessions} == {user_a.id, user_b.id}

            # Логаут user_a
            logout = await client_a.post("/api/auth/logout")
            assert logout.status_code == 204

            # Сессия user_b осталась
            sessions_after = (await db_session.execute(select(Session))).scalars().all()
            assert len(sessions_after) == 1
            assert sessions_after[0].user_id == user_b.id


async def test_logout_clears_client_cookie(
    client: AsyncClient,
    user: User,
) -> None:
    """После логаута cookie удалена из клиента."""
    await client.post(
        "/api/auth/login/email",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert SESSION_COOKIE_NAME in client.cookies

    logout = await client.post("/api/auth/logout")
    assert logout.status_code == 204

    # httpx должен применить Max-Age=0 и убрать cookie из хранилища
    assert SESSION_COOKIE_NAME not in client.cookies


async def test_login_twice_rejected(
    client: AsyncClient,
    user: User,
) -> None:
    """Второй логин без логаута → 409 (BR-AUTH-020)."""
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


async def test_login_other_user_while_authenticated(
    client: AsyncClient,
    users: list[User],
) -> None:
    """Логин под другим юзером при активной сессии → 409 (BR-AUTH-020)."""
    user_a, user_b = users[0], users[1]

    first = await client.post(
        "/api/auth/login/email",
        json={"email": user_a.email, "password": TEST_PASSWORD},
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/auth/login/email",
        json={"email": user_b.email, "password": TEST_PASSWORD},
    )
    assert second.status_code == 409


async def test_logout_then_login_as_other_user(
    client: AsyncClient,
    users: list[User],
    db_session: AsyncSession,
) -> None:
    """После логаута можно залогиниться под другим юзером."""
    user_a, user_b = users[0], users[1]

    # Логин A
    await client.post(
        "/api/auth/login/email",
        json={"email": user_a.email, "password": TEST_PASSWORD},
    )

    # Логаут
    await client.post("/api/auth/logout")

    # Логин B
    login_b = await client.post(
        "/api/auth/login/email",
        json={"email": user_b.email, "password": TEST_PASSWORD},
    )
    assert login_b.status_code == 200

    # В БД только сессия B
    sessions = (await db_session.execute(select(Session))).scalars().all()
    assert len(sessions) == 1
    assert sessions[0].user_id == user_b.id
