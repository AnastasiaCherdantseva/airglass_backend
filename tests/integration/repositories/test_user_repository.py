"""
Тесты UserRepository.

Интеграционные — используют реальную тестовую БД.
"""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.models import User
from app.repositories.user import UserRepository


async def test_get_by_email_success(db_session: AsyncSession, user: User) -> None:
    """
    get_by_email find an existing user by email
    """
    repo = UserRepository(db_session)

    found = await repo.get_by_email(user.email)

    assert found is not None
    assert found.id == user.id
    assert found.email == user.email
    assert found.name == user.name
    assert found.is_active is True
    assert found.password_hash == user.password_hash


async def test_get_by_email_not_found(db_session: AsyncSession) -> None:
    """
    get_by_email возвращает None, если пользователя с таким email нет.

    Фикстуры:
        db_session — сессия БД 
    """
    repo = UserRepository(db_session)

    found = await repo.get_by_email("nobody@example.com")

    assert found is None


async def test_get_by_id_success(db_session: AsyncSession, user: User) -> None:
    """get_by_id находит существующего пользователя."""
    repo = UserRepository(db_session)

    found = await repo.get_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert found.email == user.email
    assert found.name == user.name
    assert found.is_active is True
    assert found.password_hash == user.password_hash


async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """get_by_id возвращает None для несуществующего id."""
    repo = UserRepository(db_session)

    found = await repo.get_by_id(uuid4())

    assert found is None


async def test_get_by_email_does_not_confuse_users(
    db_session: AsyncSession, users: List[User]
) -> None:
    """get_by_email возвращает правильного пользователя."""

    repo = UserRepository(db_session)
    found = await repo.get_by_email(users[0].email)

    assert found is not None
    assert found.id == users[0].id
    assert found.email == users[0].email
    assert found.name == users[0].name
    assert found.is_active == users[0].is_active
    assert found.password_hash == users[0].password_hash

    assert found.id != users[1].id