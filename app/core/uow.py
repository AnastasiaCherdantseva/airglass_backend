"""
Unit of Work — управление транзакцией.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


class UnitOfWork:
    """
    Управляет транзакцией на HTTP-запрос.

    Не знает про репозитории и use cases — только про сессию.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._transaction: AsyncSessionTransaction | None = None

    async def begin(self) -> None:
        """Начать основную транзакцию."""
        if self._transaction is not None:
            raise RuntimeError("Transaction is already active")
        self._transaction = await self.session.begin()

    async def flush(self) -> None:
        """Отправить изменения в БД без commit."""
        await self.session.flush()

    @asynccontextmanager
    async def nested(self) -> AsyncGenerator[None, None]:
        """Создать SAVEPOINT внутри основной транзакции."""
        if self._transaction is None:
            raise RuntimeError(
                "Cannot start nested transaction without active transaction"
            )

        transaction = await self.session.begin_nested()
        try:
            yield
        except Exception:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

    async def commit(self) -> None:
        """Зафиксировать основную транзакцию."""
        if self._transaction is None:
            raise RuntimeError("No active transaction")

        await self._transaction.commit()
        self._transaction = None

    async def rollback(self) -> None:
        """Откатить основную транзакцию."""
        if self._transaction is None:
            return

        await self._transaction.rollback()
        self._transaction = None