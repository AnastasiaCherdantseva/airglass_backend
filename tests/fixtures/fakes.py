"""
Фикстуры для юнит-тестов с фейковыми репозиториями.
"""

import pytest

from app.models.system import Role, User, UserRole
from app.models.system.permission import Permission
from app.models.system.permission_condition import PermissionCondition
from app.models.system.role_permission import RolePermission
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

# -Фикстуры для фейковых репозиториев. Используют ТОЛЬКО:
# 1. users_in_memory,inactive_user_in_memory
# 2. role_in_memory, system_role_in_memory
# 3. permissions_in_memory
# 4. permission_conditions_allow_in_memory


# -По умолчанию у юзеров одна роль без прав. Только у первого в списке есть все права и роль системная
# -По умолчанию ВСЕ права имеет только системная роль


@pytest.fixture
def conditions_for_roles_in_memory(
    role_in_memory: Role,
    system_role_in_memory: Role,
    inactive_role_in_memory: Role,
    fake_permissions_repo: FakePermissionRepository,
    make_condition_in_memory,
) -> list[PermissionCondition]:
    permission = fake_permissions_repo.get_by_code_sync("USERS.CREATE")
    return [
        make_condition_in_memory(permission, type_="role", role_id=role_in_memory.id),
        make_condition_in_memory(permission, type_="role", role_id=system_role_in_memory.id),
        make_condition_in_memory(permission, type_="role", role_id=inactive_role_in_memory.id),
    ]


@pytest.fixture
def fake_users_repo(
    users_in_memory: list[User], inactive_user_in_memory: User
) -> FakeUserRepository:
    """FakeUserRepository с одним активным юзером."""
    return FakeUserRepository(users_in_memory + [inactive_user_in_memory])


@pytest.fixture
def fake_users_repo_inactive(
    inactive_user_in_memory: User,
) -> FakeUserRepository:
    """FakeUserRepository с одним неактивным юзером."""
    return FakeUserRepository([inactive_user_in_memory])


@pytest.fixture
def fake_roles_repo(
    role_in_memory: Role,
    system_role_in_memory: Role,
    inactive_role_in_memory: Role,
) -> FakeRoleRepository:
    return FakeRoleRepository([role_in_memory, system_role_in_memory, inactive_role_in_memory])


@pytest.fixture
def fake_sessions_repo() -> FakeSessionRepository:
    """Пустой FakeSessionRepository."""
    return FakeSessionRepository()


@pytest.fixture
def fake_user_roles_repo(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    role_in_memory: Role,
    system_role_in_memory: Role,
) -> FakeUserRoleRepository:
    """FakeUserRoleRepository со связью user ↔ role."""
    first_user = users_in_memory[0]
    links = [UserRole(user_id=u.id, role_id=role_in_memory.id) for u in users_in_memory]
    links.append(UserRole(user_id=first_user.id, role_id=system_role_in_memory.id))
    links.append(UserRole(user_id=inactive_user_in_memory.id, role_id=role_in_memory.id))
    return FakeUserRoleRepository(
        users=users_in_memory + [inactive_user_in_memory],
        roles=[role_in_memory, system_role_in_memory],
        links=links,
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
    conditions_for_roles_in_memory: list[PermissionCondition],
) -> FakePermissionConditionRepository:
    """FakePermissionConditionRepository с ALLOW-условиями."""
    p = permission_conditions_allow_in_memory + conditions_for_roles_in_memory
    return FakePermissionConditionRepository(p)


@pytest.fixture
def fake_role_permissions_repo(
    role_in_memory: Role,
    system_role_in_memory: Role,
    inactive_role_in_memory: Role,
    permissions_in_memory: list[Permission],
    permission_conditions_allow_in_memory: list[PermissionCondition],
    conditions_for_roles_in_memory: list[PermissionCondition],
) -> FakeRolePermissionRepository:
    """FakeRolePermissionRepository со связями role ↔ condition."""
    links = [
        RolePermission(role_id=system_role_in_memory.id, condition_id=c.id)
        for c in permission_conditions_allow_in_memory
    ]
    links.extend(
        [
            RolePermission(role_id=inactive_role_in_memory.id, condition_id=c.id)
            for c in conditions_for_roles_in_memory
            if c.role_id != role_in_memory.id
        ]
    )
    links.extend(
        [
            RolePermission(role_id=system_role_in_memory.id, condition_id=c.id)
            for c in conditions_for_roles_in_memory
        ]
    )
    condition_for_default_role = next(
        c for c in conditions_for_roles_in_memory if c.role_id == role_in_memory.id
    )
    links.append(
        RolePermission(role_id=role_in_memory.id, condition_id=condition_for_default_role.id)
    )
    p = permission_conditions_allow_in_memory + conditions_for_roles_in_memory
    return FakeRolePermissionRepository(
        roles=[role_in_memory, system_role_in_memory],
        conditions=p,
        permissions=permissions_in_memory,
        links=links,
    )


# фейковый репозиторий права-юзер (СВЯЗЕЙ ПО УМОЛЧАНИЮ НЕТ)
@pytest.fixture
def fake_user_permissions_repo(
    users_in_memory: list[User],
    role_in_memory: Role,
    inactive_user_in_memory: User,
    permissions_in_memory: list[Permission],
    permission_conditions_allow_in_memory: list[PermissionCondition],
    conditions_for_roles_in_memory: list[PermissionCondition],
) -> FakeUserPermissionRepository:
    """FakeUserPermissionRepository со связями user ↔ condition."""
    first_user = users_in_memory[0]
    other_users = users_in_memory[1:]
    conditions = permission_conditions_allow_in_memory + conditions_for_roles_in_memory
    links = [UserPermission(user_id=first_user.id, condition_id=c.id) for c in conditions]
    condition_for_default_role = next(
        c for c in conditions_for_roles_in_memory if c.role_id == role_in_memory.id
    )
    links.extend(
        [
            UserPermission(user_id=u.id, condition_id=condition_for_default_role.id)
            for u in other_users
        ]
    )
    return FakeUserPermissionRepository(
        users=users_in_memory + [inactive_user_in_memory],
        conditions=conditions,
        permissions=permissions_in_memory,
        links=links,
    )


@pytest.fixture
def fake_user_direct_permissions_repo(
    users_in_memory: list[User],
    inactive_user_in_memory: User,
    permission_conditions_allow_in_memory: list[PermissionCondition],
    conditions_for_roles_in_memory: list[PermissionCondition],
) -> FakeUserDirectPermissionRepository:
    """FakeUserDirectPermissionRepository со связями user ↔ condition."""
    p = permission_conditions_allow_in_memory + conditions_for_roles_in_memory
    return FakeUserDirectPermissionRepository(
        users=users_in_memory + [inactive_user_in_memory],
        conditions=p,
    )
