"""
Тесты UserRepository.

Интеграционные — используют реальную тестовую БД.
"""

from dataclasses import replace
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system.user import UserCreateFull, UserOutput
from app.models import User
from app.repositories.system.user import UserRepository


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
    db_session: AsyncSession, users: list[User]
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


# ─────────────────────────────────────────────────────────────
# создание
# ─────────────────────────────────────────────────────────────


async def test_create_returns_user_output(
    db_session: AsyncSession, user: User, new_user_data: UserCreateFull
) -> None:
    """create возвращает UserOutput с заполненными полями."""
    repo = UserRepository(db_session)

    result = await repo.create(new_user_data)

    assert isinstance(result, UserOutput)
    assert result.id is not None
    assert result.email == "new@example.com"
    assert result.name == "Name"
    assert result.is_active is True
    assert result.parent_id == user.id


async def test_create_persists_user_in_db(
    db_session: AsyncSession, new_user_data: UserCreateFull
) -> None:
    """После create юзер реально в БД."""
    repo = UserRepository(db_session)

    result = await repo.create(new_user_data)

    found = await repo.get_by_email(new_user_data.email)
    assert found is not None
    assert found.id == result.id


async def test_create_saves_password_hash_as_is(
    db_session: AsyncSession, new_user_data: UserCreateFull
) -> None:
    """password_hash сохраняется как есть."""
    repo = UserRepository(db_session)

    await repo.create(new_user_data)

    found = await repo.get_by_email(new_user_data.email)
    assert found is not None
    assert found.password_hash == new_user_data.password_hash


async def test_create_inactive_user(
    db_session: AsyncSession, new_user_data: UserCreateFull
) -> None:
    """is_active=False сохраняется."""
    repo = UserRepository(db_session)
    data = replace(new_user_data, is_active=False)
    result = await repo.create(data)

    assert result.is_active is False


async def test_create_duplicate_email_raises(
    db_session: AsyncSession, user: User, new_user_data: UserCreateFull
) -> None:
    """Дубликат email → IntegrityError."""
    repo = UserRepository(db_session)
    data = replace(new_user_data, email=user.email)
    with pytest.raises(IntegrityError):
        await repo.create(data)


async def test_create_duplicate_email_case_insensitive(
    db_session: AsyncSession, user: User, new_user_data: UserCreateFull
) -> None:
    """Дубликат email независимо от регистра → IntegrityError."""
    repo = UserRepository(db_session)
    data = replace(new_user_data, email=user.email.upper())

    with pytest.raises(IntegrityError):
        await repo.create(data)
