from app.models.system import PermissionAction, PermissionResource
from app.repositories.system.permission import PermissionRepository


async def test_get_by_code_found(db_session, permissions):
    """get_by_code returns DTO with correct fields for an existing permission."""
    repo = PermissionRepository(db_session)
    target = permissions[0]  # users.create

    result = await repo.get_by_code(target.code)

    assert result is not None
    assert result.id == target.id
    assert result.code == target.code
    assert result.resource == target.resource
    assert result.action == target.action
    assert result.is_system == target.is_system
    assert result.name == target.name
    assert result.description == target.description
    assert result.zone == target.zone


async def test_get_by_code_not_found(db_session, permissions):
    """get_by_code returns None for a non-existent code."""
    repo = PermissionRepository(db_session)

    result = await repo.get_by_code("nonexistent.code")

    assert result is None


async def test_get_by_code_empty_table(db_session):
    """get_by_code returns None when the table is empty."""
    repo = PermissionRepository(db_session)

    result = await repo.get_by_code("users.create")

    assert result is None


async def test_get_by_code_description_none(db_session, make_permission):
    """get_by_code handles nullable description."""
    target = await make_permission(
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
        description=None,
    )
    repo = PermissionRepository(db_session)

    result = await repo.get_by_code(target.code)

    assert result is not None
    assert result.description is None


async def test_get_by_code_returns_correct_one(db_session, permissions):
    """get_by_code returns exactly the requested permission, not another."""
    repo = PermissionRepository(db_session)
    target = permissions[5]
    other = permissions[6]

    result = await repo.get_by_code(target.code)

    assert result is not None
    assert result.id == target.id
    assert result.id != other.id
