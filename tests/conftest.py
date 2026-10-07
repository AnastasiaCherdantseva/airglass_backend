"""
Фикстуры для тестов.

Стратегия:
- engine — один на всю сессию тестов.
- create_all / drop_all — один раз на сессию.
- db_session — на каждый тест, внутри транзакции с откатом.
- client — HTTP-клиент для тестов роутеров.
"""

import os
from contextlib import asynccontextmanager
from types import TracebackType

from app.core.security import SESSION_COOKIE_NAME

os.environ["POSTGRES_DB"] = "airglass_test"
import subprocess
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.models import *  # noqa: F401,F403 — регистрирует модели в Base.metadata
from app.repositories.deps import get_uow

# Подключаем фикстуры из подпапок
pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.user_roles",
    "tests.fixtures.user_permissions",
    "tests.fixtures.user_direct_permissions",
    "tests.fixtures.sessions",
    "tests.fixtures.permissions",
    "tests.fixtures.permission_conditions",
    "tests.fixtures.roles",
    "tests.fixtures.role_permissions",
    "tests.fixtures.fakes",
    "tests.fixtures.db",
    "tests.fixtures.http",
    "tests.fixtures.organizations",
    "tests.fixtures.user_organizations",
]

TEST_DATABASE_URL = "postgresql+asyncpg://myuser:postgres@localhost:5432/airglass_test"


class FakeUnitOfWork:
    """UoW для тестов. Не управляет транзакцией."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        pass

    async def flush(self) -> None:
        await self.session.flush()

    @asynccontextmanager
    async def nested(self) -> AsyncGenerator[None, None]:
        """Savepoint внутри текущей транзакции."""
        transaction = await self.session.begin_nested()
        try:
            yield
        except Exception:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

    async def commit(self) -> None:
        """No-op. Транзакцией управляет фикстура db_session."""

    async def rollback(self) -> None:
        """No-op. Транзакцией управляет фикстура db_session."""


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


@pytest_asyncio.fixture(scope="session")
def setup_database() -> Generator[None, None, None]:
    """Применить миграции к тестовой БД."""
    alembic_ini = Path(__file__).parent.parent / "alembic.ini"

    subprocess.run(
        ["alembic", "-c", str(alembic_ini), "upgrade", "head"],
        check=True,
        env={**os.environ, "POSTGRES_DB": "airglass_test"},
        capture_output=True,
        # text=True,
    )
    yield

    subprocess.run(
        ["alembic", "-c", str(alembic_ini), "downgrade", "base"],
        check=True,
        env={**os.environ, "POSTGRES_DB": "airglass_test"},
    )


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


@pytest_asyncio.fixture(scope="function")
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
    setup_database: None,
) -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД для одного теста. Все изменения откатываются."""
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент для тестов роутеров."""

    async def override_get_uow() -> AsyncGenerator[FakeUnitOfWork, None]:
        async with FakeUnitOfWork(db_session) as uow:
            yield uow

    app.dependency_overrides[get_uow] = override_get_uow

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="https://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authorized_client(client: AsyncClient, session: dict) -> AsyncClient:
    """Клиент с cookie сессии актора (user)."""
    client.cookies.set(SESSION_COOKIE_NAME, session["token"])
    return client
