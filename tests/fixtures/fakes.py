"""
Фикстуры для юнит-тестов с фейковыми репозиториями.
"""

from uuid import uuid4

import pytest

from app.models.system import Role, User, UserRole
from tests.unit.fakes.session_repository import FakeSessionRepository
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository


@pytest.fixture
def role_in_memory() -> Role:
    """Роль в памяти (без БД)."""
    return Role(
        id=uuid4(),
        owner_id=None,
        name="Менеджер",
        description="Роль менеджера",
        is_system=False,
        is_active=True,
    )


@pytest.fixture
def fake_users_repo(user_in_memory: User) -> FakeUserRepository:
    """FakeUserRepository с одним активным юзером."""
    return FakeUserRepository([user_in_memory])


@pytest.fixture
def fake_users_repo_inactive(
    inactive_user_in_memory: User,
) -> FakeUserRepository:
    """FakeUserRepository с одним неактивным юзером."""
    return FakeUserRepository([inactive_user_in_memory])


@pytest.fixture
def fake_sessions_repo() -> FakeSessionRepository:
    """Пустой FakeSessionRepository."""
    return FakeSessionRepository()


@pytest.fixture
def fake_user_roles_repo(
    user_in_memory: User,
    role_in_memory: Role,
) -> FakeUserRoleRepository:
    """FakeUserRoleRepository со связью user ↔ role."""
    link = UserRole(user_id=user_in_memory.id, role_id=role_in_memory.id)
    return FakeUserRoleRepository(
        users=[user_in_memory],
        roles=[role_in_memory],
        links=[link],
    )
