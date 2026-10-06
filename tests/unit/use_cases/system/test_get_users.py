from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from app.dto import UserListOutput, UserRoleLink
from app.models.system import Role, User
from app.use_cases.system.get_users import get_users
from tests.unit.fakes.user_repository import FakeUserRepository
from tests.unit.fakes.user_role_repository import FakeUserRoleRepository

MakeUser = Callable[..., User]
MakeUsersRepo = Callable[..., FakeUserRepository]


async def _call(
    owner_id: UUID,
    users: FakeUserRepository,
    user_roles: FakeUserRoleRepository,
    *,
    limit: int = 10,
    page: int = 0,
) -> UserListOutput:
    """
    Call get_users and assert the result is not None.

    Вызывает get_users и проверяет, что результат не None.
    """
    result = await get_users(owner_id, limit, page, users=users, user_roles=user_roles)
    assert result is not None
    return result


async def _give_role(repo: FakeUserRoleRepository, user: User, role: Role) -> None:
    """
    Link a role to a user in the fake repository.

    Привязывает роль к пользователю в фейковом репозитории.
    """
    await repo.add_link(UserRoleLink(user_id=user.id, role_id=role.id))


# ─────────────────────────────────────────────────────────────
# 1-3. Basic results
# ─────────────────────────────────────────────────────────────


async def test_no_children_returns_empty(
    users_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    No children -> empty items, total=0, limit/page echoed back.

    Нет детей -> пустой items, total=0, limit/page как переданы.
    """
    actor = users_in_memory[1]

    result = await _call(actor.id, make_users_repo(), fake_user_roles_repo, limit=7, page=3)

    assert result.items == []
    assert result.total == 0
    assert result.limit == 7
    assert result.page == 3


async def test_one_child(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    One direct child -> one item, total=1.

    Один прямой ребёнок -> один элемент, total=1.
    """
    child = children_user_admin_in_memory[0]

    result = await _call(user_admin_in_memory.id, make_users_repo(child), fake_user_roles_repo)

    assert [i.id for i in result.items] == [child.id]
    assert result.total == 1


async def test_several_children_no_pagination(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Three children, limit=10, page=0 -> all three, total=3.

    Три ребёнка, limit=10, page=0 -> все три, total=3.
    """
    children = children_user_admin_in_memory[:3]

    result = await _call(
        user_admin_in_memory.id,
        make_users_repo(*children),
        fake_user_roles_repo,
        limit=10,
        page=0,
    )

    assert [i.id for i in result.items] == [c.id for c in children]
    assert result.total == 3


# ─────────────────────────────────────────────────────────────
# 4-6. Pagination
# ─────────────────────────────────────────────────────────────


async def test_pagination_first_page(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Five children, limit=2, page=0 -> first two, total=5.

    Пять детей, limit=2, page=0 -> первые два, total=5.
    """
    result = await _call(
        user_admin_in_memory.id,
        make_users_repo(*children_user_admin_in_memory),
        fake_user_roles_repo,
        limit=2,
        page=0,
    )

    assert [i.id for i in result.items] == [c.id for c in children_user_admin_in_memory[0:2]]
    assert result.total == 5
    assert (result.limit, result.page) == (2, 0)


async def test_pagination_second_page(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Five children, limit=2, page=1 -> the next two, total=5.

    Пять детей, limit=2, page=1 -> следующие два, total=5.
    """
    result = await _call(
        user_admin_in_memory.id,
        make_users_repo(*children_user_admin_in_memory),
        fake_user_roles_repo,
        limit=2,
        page=1,
    )

    assert [i.id for i in result.items] == [c.id for c in children_user_admin_in_memory[2:4]]
    assert result.total == 5
    assert (result.limit, result.page) == (2, 1)


async def test_pagination_empty_page_keeps_total(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Page beyond the end -> items=[], but total is still 5.

    Страница за пределами -> items=[], но total по-прежнему 5.
    """
    result = await _call(
        user_admin_in_memory.id,
        make_users_repo(*children_user_admin_in_memory),
        fake_user_roles_repo,
        limit=2,
        page=10,
    )

    assert result.items == []
    assert result.total == 5
    assert (result.limit, result.page) == (2, 10)


# ─────────────────────────────────────────────────────────────
# 7-8, 12. Filtering
# ─────────────────────────────────────────────────────────────


async def test_only_direct_children(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_user_in_memory: MakeUser,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Actor -> child -> grandchild: only the child is returned.

    Актор -> ребёнок -> внук: возвращается только ребёнок.
    """
    child = children_user_admin_in_memory[0]
    grandchild = make_user_in_memory(email="grandchild@example.com", parent_id=child.id)

    result = await _call(
        user_admin_in_memory.id, make_users_repo(child, grandchild), fake_user_roles_repo
    )

    assert [i.id for i in result.items] == [child.id]
    assert result.total == 1


async def test_soft_deleted_are_excluded(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_user_in_memory: MakeUser,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Soft-deleted child is neither in items nor in total.

    Мягко удалённый ребёнок не попадает ни в items, ни в total.
    """
    alive = children_user_admin_in_memory[:2]
    deleted = make_user_in_memory(
        email="deleted@example.com",
        parent_id=user_admin_in_memory.id,
        deleted_at=datetime.now(UTC),
    )

    result = await _call(
        user_admin_in_memory.id, make_users_repo(*alive, deleted), fake_user_roles_repo
    )

    assert {i.id for i in result.items} == {c.id for c in alive}
    assert deleted.id not in {i.id for i in result.items}
    assert result.total == 2


async def test_other_parents_children_are_isolated(
    users_in_memory: list[User],
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    make_user_in_memory: MakeUser,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Children of another parent are not returned.

    Дети другого родителя не попадают в результат.
    """
    other_parent = users_in_memory[1]
    foreign = [
        make_user_in_memory(email=f"foreign{i}@example.com", parent_id=other_parent.id)
        for i in range(2)
    ]

    result = await _call(
        user_admin_in_memory.id,
        make_users_repo(*children_user_admin_in_memory, *foreign),
        fake_user_roles_repo,
    )

    ids = {i.id for i in result.items}
    assert ids == {c.id for c in children_user_admin_in_memory}
    assert ids.isdisjoint({f.id for f in foreign})
    assert result.total == 5


# ─────────────────────────────────────────────────────────────
# 9-11. Roles
# ─────────────────────────────────────────────────────────────


async def test_roles_are_attached(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    role_in_memory: Role,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Child's role ends up in role_ids.

    Роль ребёнка попадает в role_ids.
    """
    child = children_user_admin_in_memory[0]
    await _give_role(fake_user_roles_repo, child, role_in_memory)

    result = await _call(user_admin_in_memory.id, make_users_repo(child), fake_user_roles_repo)

    assert result.items[0].role_ids == [role_in_memory.id]


async def test_each_child_has_own_roles(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    role_in_memory: Role,
    system_role_in_memory: Role,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Different children with different roles: role_ids are not mixed up.

    Дети с разными ролями: role_ids не перемешиваются.
    """
    first, second, third = children_user_admin_in_memory[:3]
    await _give_role(fake_user_roles_repo, first, role_in_memory)
    await _give_role(fake_user_roles_repo, second, system_role_in_memory)
    await _give_role(fake_user_roles_repo, third, role_in_memory)
    await _give_role(fake_user_roles_repo, third, system_role_in_memory)

    result = await _call(
        user_admin_in_memory.id, make_users_repo(first, second, third), fake_user_roles_repo
    )

    by_id = {i.id: set(i.role_ids) for i in result.items}
    assert by_id == {
        first.id: {role_in_memory.id},
        second.id: {system_role_in_memory.id},
        third.id: {role_in_memory.id, system_role_in_memory.id},
    }


async def test_child_without_roles_gets_empty_list(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    role_in_memory: Role,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    Child without roles -> role_ids=[] (no KeyError).

    Ребёнок без ролей -> role_ids=[] (без KeyError).
    """
    with_role, without_role = children_user_admin_in_memory[:2]
    await _give_role(fake_user_roles_repo, with_role, role_in_memory)

    result = await _call(
        user_admin_in_memory.id, make_users_repo(with_role, without_role), fake_user_roles_repo
    )

    by_id = {i.id: i.role_ids for i in result.items}
    assert by_id[without_role.id] == []
    assert by_id[with_role.id] == [role_in_memory.id]


# ─────────────────────────────────────────────────────────────
# 13. Output fields
# ─────────────────────────────────────────────────────────────


async def test_output_fields_are_filled(
    user_admin_in_memory: User,
    children_user_admin_in_memory: list[User],
    role_in_memory: Role,
    make_user_in_memory: MakeUser,
    make_users_repo: MakeUsersRepo,
    fake_user_roles_repo: FakeUserRoleRepository,
) -> None:
    """
    All UserWithRolesOutput fields are filled, including children_count.

    Все поля UserWithRolesOutput заполнены, включая children_count.
    """
    child = children_user_admin_in_memory[0]
    grandchild = make_user_in_memory(email="grandchild@example.com", parent_id=child.id)
    await _give_role(fake_user_roles_repo, child, role_in_memory)

    result = await _call(
        user_admin_in_memory.id, make_users_repo(child, grandchild), fake_user_roles_repo
    )

    item = result.items[0]
    assert item.id == child.id
    assert item.parent_id == user_admin_in_memory.id
    assert item.email == child.email
    assert item.name == child.name
    assert item.is_active == child.is_active
    assert item.children_count == 1
    assert item.role_ids == [role_in_memory.id]
