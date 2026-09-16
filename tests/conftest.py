"""
Фикстуры для тестов.

Стратегия:
- engine — один на всю сессию тестов.
- create_all / drop_all — один раз на сессию.
- db_session — на каждый тест, внутри транзакции с откатом.
- client — HTTP-клиент для тестов роутеров.
"""

from collections.abc import AsyncGenerator

from uuid import uuid4
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.database import get_db
from app.main import app
from app.models.base import Base
from app.models import *  # noqa: F401,F403 — регистрирует модели в Base.metadata


TEST_DATABASE_URL = (
    "postgresql+asyncpg://myuser:postgres@localhost:5432/airglass_test"
)


# ============================================
# ENGINE — один на сессию
# ============================================

@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Движок БД для тестов. Один на всю сессию."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


# ============================================
# ТАБЛИЦЫ — один раз на сессию
# ============================================

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Создаёт таблицы до тестов, удаляет после — один раз на сессию."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# ============================================
# USER — готовый пользователь в БД
# ============================================

@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    """Готовый активный пользователь в БД."""
    user = User(
        id=uuid4(),
        name="Аня",
        email="anya@example.com",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user

@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Неактивный пользователь."""
    user = User(
        id=uuid4(),
        name="Иван",
        email="ivan@example.com",
        password_hash="hash",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user

@pytest_asyncio.fixture
async def users(db_session: AsyncSession) -> list[User]:
    """Несколько пользователей для тестов пагинации."""
    users = [
        User(
            id=uuid4(),
            name=f"User{i}",
            email=f"user{i}@example.com",
            password_hash="hash",
            is_active=True,
        )
        for i in range(5)
    ]
    db_session.add_all(users)
    await db_session.flush()
    return users

# ============================================
# SESSION FACTORY — один на сессию
# ============================================

@pytest_asyncio.fixture(scope="session")
async def session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Фабрика сессий. Одна на всю сессию."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# ============================================
# DB SESSION — на каждый тест, с откатом
# ============================================

@pytest_asyncio.fixture(scope="function")
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Сессия БД для одного теста.

    Все изменения откатываются после теста — БД остаётся чистой.
    """
    async with session_factory() as session:
        yield session
        await session.rollback()


# ============================================
# HTTP CLIENT — на каждый тест
# ============================================

@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP-клиент для тестов роутеров.

    Подменяет `get_db` на тестовую сессию.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()