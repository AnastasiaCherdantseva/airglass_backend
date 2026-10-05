"""
Unit of Work — управление транзакцией.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


class UnitOfWork:
    """
    Управляет транзакцией на HTTP-запрос.

    Не знает про репозитории и use cases — только про сессию.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._transaction: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self._transaction = await self.session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self._commit()

    async def flush(self) -> None:
        """Отправить изменения в БД без commit."""
        await self.session.flush()

    @asynccontextmanager
    async def nested(self) -> AsyncGenerator[None, None]:
        """Создать SAVEPOINT внутри основной транзакции."""
        if self._transaction is None:
            raise RuntimeError("Cannot start nested transaction without active transaction")

        transaction = await self.session.begin_nested()
        try:
            yield
        except Exception:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

    async def _commit(self) -> None:
        """Зафиксировать основную транзакцию."""
        if self._transaction is None:
            return
            # raise RuntimeError("No active transaction")

        await self._transaction.commit()
        self._transaction = None

    async def rollback(self) -> None:
        """Откатить основную транзакцию."""
        if self._transaction is None:
            return

        await self._transaction.rollback()
        self._transaction = None
