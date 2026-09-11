"""
Фикстуры для тестов.
"""

import asyncio
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models.base import Base
from app.models import *  # noqa — импорт всех моделей


# ============================================
# ТЕСТОВАЯ БД
# ============================================

TEST_DATABASE_URL = (
    "postgresql+asyncpg://myuser:postgres@localhost:5433/airglass_test"
)




# ============================================
# ДВИЖОК
# ============================================

@pytest_asyncio.fixture(scope="session")
async def engine():
    """Движок БД для тестов."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


# ============================================
# СЕССИЯ
# ============================================

@pytest_asyncio.fixture(scope="function")
async def db(engine):
    """
    Сессия БД для одного теста.
    
    Создаёт таблицы перед тестом, удаляет после.
    """
    # Создать таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создать сессию
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
    
    # Удалить таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)