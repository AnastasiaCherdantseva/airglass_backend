"""
Фикстуры для юнит-тестов с фейковыми репозиториями.
"""

from uuid import uuid4

import pytest

from app.models.system import Role, User, UserRole
from app.models.system.permission import Permission
from app.models.system.permission_condition import PermissionCondition
from app.models.system.role_permission import RolePermission
from app.models.system.user_direct_permission import UserDirectPermission
from app.models.system.user_permission import UserPermission
from tests.unit.fakes.permission import FakePermissionRepository
from tests.unit.fakes.permission_condition import FakePermissionConditionRepository
from tests.unit.fakes.role import FakeRoleRepository
from tests.unit.fakes.role_permission import FakeRolePermissionRepository
from tests.unit.fakes.session_repository import FakeSessionRepository
from tests.unit.fakes.user_direct_permission import FakeUserDirectPermissionRepository
from tests.unit.fakes.user_permission import FakeUserPermissionRepository
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


@pytest.fixture
def fake_permissions_repo(
    permissions_in_memory: list[Permission],
) -> FakePermissionRepository:
    """FakePermissionRepository со всеми permissions."""
    return FakePermissionRepository(permissions_in_memory)


@pytest.fixture
def fake_permission_conditions_repo(
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> FakePermissionConditionRepository:
    """FakePermissionConditionRepository с ALLOW-условиями."""
    return FakePermissionConditionRepository(permission_conditions_allow_in_memory)


@pytest.fixture
def fake_roles_repo(
    role_in_memory: Role,
) -> FakeRoleRepository:
    """FakeRoleRepository с одной ролью."""
    return FakeRoleRepository([role_in_memory])


@pytest.fixture
def fake_roles_repo_system(
    system_role_in_memory: Role,
) -> FakeRoleRepository:
    """FakeRoleRepository с одной системной ролью."""
    return FakeRoleRepository([system_role_in_memory])


@pytest.fixture
def fake_role_permissions_repo(
    role_in_memory: Role,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> FakeRolePermissionRepository:
    """FakeRolePermissionRepository со связями role ↔ condition."""
    links = [
        RolePermission(role_id=role_in_memory.id, condition_id=c.id)
        for c in permission_conditions_allow_in_memory
    ]
    return FakeRolePermissionRepository(links)


@pytest.fixture
def fake_user_permissions_repo(
    user_in_memory: User,
    permissions_in_memory: list[Permission],
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> FakeUserPermissionRepository:
    """FakeUserPermissionRepository со связями user ↔ condition."""
    conditions = {c.id: c for c in permission_conditions_allow_in_memory}
    permissions = {p.id: p for p in permissions_in_memory}
    links = [
        UserPermission(
            user_id=user_in_memory.id,
            condition_id=c.id,
        )
        for c in permission_conditions_allow_in_memory
    ]
    return FakeUserPermissionRepository(
        conditions=conditions,
        permissions=permissions,
        links=links,
    )


@pytest.fixture
def fake_user_direct_permissions_repo(
    user_in_memory: User,
    permission_conditions_allow_in_memory: list[PermissionCondition],
) -> FakeUserDirectPermissionRepository:
    """FakeUserDirectPermissionRepository со связями user ↔ condition."""
    links = [
        UserDirectPermission(
            user_id=user_in_memory.id,
            condition_id=c.id,
        )
        for c in permission_conditions_allow_in_memory
    ]
    return FakeUserDirectPermissionRepository(links)
