"""
Репозиторий пользователей.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.base import BaseIdRepository
from uuid import UUID

class UserRepository(BaseIdRepository[User]):
    """
    SQLAlchemy-реализация репозитория аутентификации пользователей.

    Наследует get_by_id, add, delete, flush от BaseIdRepository.
    Добавляет get_by_email
    """

    model = User

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

