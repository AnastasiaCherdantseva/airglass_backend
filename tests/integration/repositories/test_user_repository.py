"""
Тесты UserRepository.

Интеграционные — используют реальную тестовую БД.
"""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system.user import UserCreateFull, UserOutput, UserPatchInput
from app.models import User
from app.repositories.system.user import UserRepository


@pytest_asyncio.fixture
async def tree(user: User, users: list[User], make_user) -> SimpleNamespace:
    """User hierarchy: root -> (child_a -> grandchild -> great, child_b); separate outsider branch.

    Иерархия: root -> (child_a -> grandchild -> great, child_b); отдельная ветка outsider.
    """
    child_a = await make_user(email="a@example.com", parent_id=user.id)
    child_b = await make_user(email="b@example.com", parent_id=user.id)
    grandchild = await make_user(email="a1@example.com", parent_id=child_a.id)
    great = await make_user(email="a11@example.com", parent_id=grandchild.id)
    outsider = users[0]
    outsider_child = await make_user(email="o1@example.com", parent_id=outsider.id)
    return SimpleNamespace(
        root=user,
        child_a=child_a,
        child_b=child_b,
        grandchild=grandchild,
        great=great,
        outsider=outsider,
        outsider_child=outsider_child,
    )


async def _reload(db_session: AsyncSession, *objs: User) -> None:
    """Re-read rows from the DB.

    Перечитать строки из БД.
    """
    for obj in objs:
        await db_session.refresh(obj)


async def _make_children(make_user, parent: User, count: int = 5) -> list[User]:
    """Create direct children with ascending created_at.

    Создать прямых детей с возрастающим created_at.
    """
    base = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        await make_user(
            email=f"c{i}@example.com",
            parent_id=parent.id,
            created_at=base + timedelta(minutes=i),
            email_verified=datetime.now(UTC),
        )
        for i in range(count)
    ]


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


# ─────────────────────────────────────────────────────────────
# count_by_parent_id
# ─────────────────────────────────────────────────────────────


async def test_count_by_parent_id_returns_zero(
    db_session: AsyncSession,
    user: User,
) -> None:
    """Нет детей → 0."""
    repo = UserRepository(db_session)

    result = await repo.count_by_parent_id(user.id)

    assert result == 0


async def test_count_by_parent_id_returns_correct_number(
    db_session: AsyncSession,
    user: User,
    make_user,
) -> None:
    """Три прямых ребёнка → 3."""
    for i in range(3):
        await make_user(
            email=f"child{i}@example.com",
            parent_id=user.id,
        )
    repo = UserRepository(db_session)

    result = await repo.count_by_parent_id(user.id)

    assert result == 3


async def test_count_by_parent_id_counts_only_direct_children(
    db_session: AsyncSession,
    user: User,
    make_user,
) -> None:
    """Внуки не считаются."""
    child = await make_user(email="child@example.com", parent_id=user.id)
    await make_user(email="grandchild@example.com", parent_id=child.id)
    repo = UserRepository(db_session)

    result = await repo.count_by_parent_id(user.id)

    assert result == 1


async def test_count_by_parent_id_skips_deleted(
    db_session: AsyncSession,
    user: User,
    make_user,
) -> None:
    """Мягко удалённые дети не считаются."""
    from datetime import UTC, datetime

    alive = await make_user(email="alive@example.com", parent_id=user.id)
    deleted = await make_user(email="deleted@example.com", parent_id=user.id)
    deleted.deleted_at = datetime.now(UTC)
    await db_session.flush()
    repo = UserRepository(db_session)

    result = await repo.count_by_parent_id(user.id)

    assert result == 1


async def test_count_by_parent_id_isolated_by_parent(
    db_session: AsyncSession,
    users: list[User],
    make_user,
) -> None:
    """Дети других родителей не считаются."""
    parent_a, parent_b = users[0], users[1]
    for i in range(2):
        await make_user(email=f"a{i}@example.com", parent_id=parent_a.id)
    for i in range(3):
        await make_user(email=f"b{i}@example.com", parent_id=parent_b.id)
    repo = UserRepository(db_session)

    result_a = await repo.count_by_parent_id(parent_a.id)
    result_b = await repo.count_by_parent_id(parent_b.id)

    assert result_a == 2
    assert result_b == 3


# ─────────────────────────────────────────────────────────────
# count_children_by_parent_ids
# ─────────────────────────────────────────────────────────────


async def test_count_children_by_parent_ids_empty_input(
    db_session: AsyncSession,
) -> None:
    """Пустой список → пустой словарь, без запроса в БД."""
    repo = UserRepository(db_session)

    result = await repo._count_children_by_parent_ids([])

    assert result == {}


async def test_count_children_by_parent_ids_returns_counts(
    db_session: AsyncSession,
    users: list[User],
    make_user,
) -> None:
    """Для двух родителей — правильные счётчики."""
    parent_a, parent_b = users[0], users[1]
    for i in range(3):
        await make_user(email=f"a{i}@example.com", parent_id=parent_a.id)
    for i in range(2):
        await make_user(email=f"b{i}@example.com", parent_id=parent_b.id)
    repo = UserRepository(db_session)

    result = await repo._count_children_by_parent_ids([parent_a.id, parent_b.id])

    assert result == {parent_a.id: 3, parent_b.id: 2}


async def test_count_children_by_parent_ids_missing_parent(
    db_session: AsyncSession,
    user: User,
) -> None:
    """Родитель без детей → {user.id: 0}."""
    repo = UserRepository(db_session)

    result = await repo._count_children_by_parent_ids([user.id])

    assert result == {user.id: 0}


async def test_count_children_by_parent_ids_skips_deleted(
    db_session: AsyncSession,
    user: User,
    make_user,
) -> None:
    """Мягко удалённые дети не считаются."""
    from datetime import UTC, datetime

    await make_user(email="alive@example.com", parent_id=user.id)
    deleted = await make_user(email="deleted@example.com", parent_id=user.id)
    deleted.deleted_at = datetime.now(UTC)
    await db_session.flush()
    repo = UserRepository(db_session)

    result = await repo._count_children_by_parent_ids([user.id])

    assert result == {user.id: 1}


async def test_count_children_by_parent_ids_only_direct(
    db_session: AsyncSession,
    user: User,
    make_user,
) -> None:
    """Внуки не считаются."""
    child = await make_user(email="child@example.com", parent_id=user.id)
    await make_user(email="grandchild@example.com", parent_id=child.id)
    repo = UserRepository(db_session)

    result = await repo._count_children_by_parent_ids([user.id])

    assert result == {user.id: 1}


async def test_get_by_email_ignores_case_and_whitespace(
    db_session: AsyncSession, make_user
) -> None:
    """Lookup is case-insensitive and trims whitespace (ADR-USER-002).

    Поиск не зависит от регистра и обрезает пробелы (ADR-USER-002).
    """
    stored = await make_user(email="Mixed.Case@Example.com")

    found = await UserRepository(db_session).get_by_email("  MIXED.case@example.COM ")

    assert found is not None
    assert found.id == stored.id


async def test_get_by_email_skips_soft_deleted(db_session: AsyncSession, make_user) -> None:
    """Soft-deleted user is not found by email.

    Мягко удалённый пользователь не находится по email.
    """
    deleted = await make_user(email="gone@example.com", deleted_at=datetime.now(UTC))

    assert await UserRepository(db_session).get_by_email(deleted.email) is None


async def test_get_by_id_skips_soft_deleted(db_session: AsyncSession, make_user) -> None:
    """Soft-deleted user is not returned by id.

    Мягко удалённый пользователь не возвращается по id.
    """
    deleted = await make_user(email="gone@example.com", deleted_at=datetime.now(UTC))

    assert await UserRepository(db_session).get_by_id(deleted.id) is None


async def test_create_lowercases_email(
    db_session: AsyncSession, new_user_data: UserCreateFull
) -> None:
    """Email is stored in lower case.

    Email сохраняется в нижнем регистре.
    """
    data = replace(new_user_data, email="  New.User@Example.COM ")

    result = await UserRepository(db_session).create(data)

    assert result.email == "new.user@example.com"


async def test_create_reuses_email_of_soft_deleted_user(
    db_session: AsyncSession, make_user, new_user_data: UserCreateFull
) -> None:
    """Email of a soft-deleted user can be taken again (partial unique index).

    Email мягко удалённого пользователя можно занять снова (частичный unique-индекс).
    """
    deleted = await make_user(email="reuse@example.com", deleted_at=datetime.now(UTC))

    result = await UserRepository(db_session).create(
        replace(new_user_data, email="reuse@example.com")
    )

    assert result.id != deleted.id


# ── get_by_parent_id ──────────────────────────────────────────────────


async def test_get_by_parent_id_empty(db_session: AsyncSession, user: User) -> None:
    """No children -> empty list.

    Нет детей -> пустой список.
    """
    assert await UserRepository(db_session).get_by_parent_id(user.id) == []


@pytest.mark.parametrize("page", [0, 1, 2, 5])
async def test_get_by_parent_id_pagination_and_order(
    db_session: AsyncSession, user: User, make_user, page: int
) -> None:
    """Pages follow created_at order; a page past the end is empty.

    Страницы идут в порядке created_at; страница за пределами пуста.
    """
    children = await _make_children(make_user, user)

    result = await UserRepository(db_session).get_by_parent_id(user.id, limit=2, page=page)

    assert [u.id for u in result] == [c.id for c in children[page * 2 : page * 2 + 2]]


async def test_get_by_parent_id_output_fields(
    db_session: AsyncSession, user: User, make_user
) -> None:
    """DTO fields are filled, children_count counts grandchildren.

    Поля DTO заполнены, children_count считает внуков.
    """
    child = (await _make_children(make_user, user, 1))[0]
    await make_user(email="gc@example.com", parent_id=child.id)

    [item] = await UserRepository(db_session).get_by_parent_id(user.id)

    assert item == UserOutput(
        id=child.id,
        parent_id=user.id,
        email=child.email,
        name=child.name,
        is_active=child.is_active,
        children_count=1,
        email_verified=True,
    )


async def test_get_by_parent_id_excludes_deleted_and_indirect(
    db_session: AsyncSession, user: User, make_user
) -> None:
    """Soft-deleted children and grandchildren are not returned.

    Мягко удалённые дети и внуки не возвращаются.
    """
    child = await make_user(
        email="child@example.com", parent_id=user.id, email_verified=datetime.now(UTC)
    )
    await make_user(
        email="deleted@example.com",
        parent_id=user.id,
        email_verified=datetime.now(UTC),
        deleted_at=datetime.now(UTC),
    )
    await make_user(
        email="grandchild@example.com", parent_id=child.id, email_verified=datetime.now(UTC)
    )

    result = await UserRepository(db_session).get_by_parent_id(user.id)

    assert [u.id for u in result] == [child.id]


async def test_get_by_parent_id_children_count_skips_deleted(
    db_session: AsyncSession, user: User, make_user
) -> None:
    """children_count does not include soft-deleted grandchildren.

    children_count не учитывает мягко удалённых внуков.
    """
    child = await make_user(email="child@example.com", parent_id=user.id)
    await make_user(email="alive@example.com", parent_id=child.id)
    await make_user(email="gone@example.com", parent_id=child.id, deleted_at=datetime.now(UTC))

    [item] = await UserRepository(db_session).get_by_parent_id(user.id)

    assert item.children_count == 1


async def test_get_by_parent_id_isolated(
    db_session: AsyncSession, users: list[User], make_user
) -> None:
    """Children of another parent are not returned.

    Дети другого родителя не возвращаются.
    """
    mine = await make_user(email="mine@example.com", parent_id=users[0].id)
    await make_user(email="other@example.com", parent_id=users[1].id)

    result = await UserRepository(db_session).get_by_parent_id(users[0].id)

    assert [u.id for u in result] == [mine.id]


# ── get_subtree ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        pytest.param(
            "root", {"root", "child_a", "child_b", "grandchild", "great"}, id="root_all_levels"
        ),
        pytest.param("child_a", {"child_a", "grandchild", "great"}, id="branch"),
        pytest.param("grandchild", {"grandchild", "great"}, id="middle"),
        pytest.param("great", {"great"}, id="leaf_is_itself"),
        pytest.param("child_b", {"child_b"}, id="sibling_branch_excluded"),
    ],
)
async def test_get_subtree(
    db_session: AsyncSession, tree: SimpleNamespace, start: str, expected: set[str]
) -> None:
    """Subtree = node + all descendants; ancestors, siblings and other branches are excluded.

    Поддерево = узел + все потомки; предки, братья и чужие ветки не входят.
    """
    result = await UserRepository(db_session).get_subtree(getattr(tree, start).id)

    assert {u.id for u in result} == {getattr(tree, n).id for n in expected}


async def test_get_subtree_unknown_id(db_session: AsyncSession) -> None:
    """Unknown id -> empty list.

    Неизвестный id -> пустой список.
    """
    assert await UserRepository(db_session).get_subtree(uuid4()) == []


async def test_get_subtree_deleted_root_is_empty(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """Soft-deleted anchor -> empty list.

    Мягко удалённый корень -> пустой список.
    """
    tree.child_a.deleted_at = datetime.now(UTC)
    await db_session.flush()

    assert await UserRepository(db_session).get_subtree(tree.child_a.id) == []


async def test_get_subtree_deleted_node_cuts_branch(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """A soft-deleted node cuts off itself and its whole branch.

    Мягко удалённый узел отсекает себя и всю свою ветку.
    """
    tree.grandchild.deleted_at = datetime.now(UTC)
    await db_session.flush()

    result = await UserRepository(db_session).get_subtree(tree.root.id)

    assert {u.id for u in result} == {tree.root.id, tree.child_a.id, tree.child_b.id}


# ── is_in_subtree ─────────────────────────────────────────────────────


@pytest.mark.parametrize("name", ["root", "child_a", "grandchild", "great"])
async def test_is_in_subtree_self_and_descendants(
    db_session: AsyncSession, tree: SimpleNamespace, name: str
) -> None:
    """Root itself and descendants of any depth are in the subtree.

    Сам корень и потомки любой глубины входят в поддерево.
    """
    assert await UserRepository(db_session).is_in_subtree(tree.root.id, getattr(tree, name).id)


@pytest.mark.parametrize(
    ("root", "target"),
    [
        pytest.param("child_a", "root", id="ancestor"),
        pytest.param("grandchild", "child_a", id="parent_of_root"),
        pytest.param("child_a", "child_b", id="sibling"),
        pytest.param("root", "outsider", id="other_tree"),
        pytest.param("root", "outsider_child", id="other_tree_child"),
    ],
)
async def test_is_in_subtree_false(
    db_session: AsyncSession, tree: SimpleNamespace, root: str, target: str
) -> None:
    """Ancestors, siblings and other branches are not in the subtree.

    Предки, братья и чужие ветки не входят в поддерево.
    """
    result = await UserRepository(db_session).is_in_subtree(
        getattr(tree, root).id, getattr(tree, target).id
    )

    assert result is False


async def test_is_in_subtree_unknown_ids(db_session: AsyncSession) -> None:
    """Unknown ids -> False.

    Неизвестные id -> False.
    """
    assert await UserRepository(db_session).is_in_subtree(uuid4(), uuid4()) is False


async def test_is_in_subtree_deleted_target_and_branch(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """Soft-deleted target and its descendants are not in the subtree.

    Мягко удалённая цель и её потомки не входят в поддерево.
    """
    tree.child_a.deleted_at = datetime.now(UTC)
    await db_session.flush()
    repo = UserRepository(db_session)

    assert await repo.is_in_subtree(tree.root.id, tree.child_a.id) is False
    assert await repo.is_in_subtree(tree.root.id, tree.grandchild.id) is False
    assert await repo.is_in_subtree(tree.root.id, tree.child_b.id) is True


async def test_is_in_subtree_deleted_root(db_session: AsyncSession, tree: SimpleNamespace) -> None:
    """Soft-deleted root -> False for everyone.

    Мягко удалённый корень -> False для всех.
    """
    tree.root.deleted_at = datetime.now(UTC)
    await db_session.flush()

    assert await UserRepository(db_session).is_in_subtree(tree.root.id, tree.child_a.id) is False


# ── soft_delete_by_id ─────────────────────────────────────────────────


async def test_soft_delete_marks_whole_subtree(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """Subtree is deactivated with one shared deleted_at; the rest is untouched.

    Поддерево деактивируется с общим deleted_at; остальные не затронуты.
    """
    deleted = [tree.child_a, tree.grandchild, tree.great]
    untouched = [tree.root, tree.child_b, tree.outsider, tree.outsider_child]

    count = await UserRepository(db_session).soft_delete_by_id(tree.child_a.id)

    await _reload(db_session, *deleted, *untouched)
    assert count == 3
    assert all(u.deleted_at is not None and u.is_active is False for u in deleted)
    assert len({u.deleted_at for u in deleted}) == 1
    assert all(u.deleted_at is None and u.is_active is True for u in untouched)


async def test_soft_delete_unknown_id(db_session: AsyncSession, tree: SimpleNamespace) -> None:
    """Unknown id -> 0, nothing changes.

    Неизвестный id -> 0, ничего не меняется.
    """
    count = await UserRepository(db_session).soft_delete_by_id(uuid4())

    await _reload(db_session, tree.root)
    assert count == 0
    assert tree.root.deleted_at is None


async def test_soft_delete_twice_is_noop(db_session: AsyncSession, tree: SimpleNamespace) -> None:
    """Second call on the same target returns 0.

    Повторный вызов для той же цели возвращает 0.
    """
    repo = UserRepository(db_session)
    await repo.soft_delete_by_id(tree.child_a.id)

    assert await repo.soft_delete_by_id(tree.child_a.id) == 0


async def test_soft_delete_keeps_earlier_deleted_at(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """Already deleted descendants keep their original deleted_at.

    У ранее удалённых потомков deleted_at не перезаписывается.
    """
    repo = UserRepository(db_session)
    await repo.soft_delete_by_id(tree.grandchild.id)
    await _reload(db_session, tree.grandchild)
    first = tree.grandchild.deleted_at

    count = await repo.soft_delete_by_id(tree.child_a.id)

    await _reload(db_session, tree.grandchild)
    assert count == 1
    assert tree.grandchild.deleted_at == first


async def test_soft_deleted_users_disappear_from_reads(
    db_session: AsyncSession, tree: SimpleNamespace
) -> None:
    """After deletion the user is hidden from email lookup, children list and counter.

    После удаления пользователь скрыт из поиска по email, списка детей и счётчика.
    """
    repo = UserRepository(db_session)

    await repo.soft_delete_by_id(tree.child_a.id)

    assert await repo.get_by_email(tree.child_a.email) is None
    assert [u.id for u in await repo.get_by_parent_id(tree.root.id)] == [tree.child_b.id]
    assert await repo.count_by_parent_id(tree.root.id) == 1


# ── patch_user ────────────────────────────────────────────────────────


def _patch(user_id, **fields) -> UserPatchInput:
    """Build UserPatchInput with all unspecified fields set to None.

    Собрать UserPatchInput, неуказанные поля = None.
    """
    return UserPatchInput(
        **{"id": user_id, "email": None, "name": None, "new_password_hash": None, **fields}
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("name", "Новое имя", id="name"),
        pytest.param("email", "other@example.com", id="email"),
        pytest.param("new_password_hash", "new-hash", id="password_hash"),
    ],
)
async def test_patch_user_updates_single_field(
    db_session: AsyncSession, user: User, field: str, value: str
) -> None:
    """Only the given field changes in the DB.

    В БД меняется только переданное поле.
    """
    expected = {"name": user.name, "email": user.email, "new_password_hash": user.password_hash}
    expected[field] = value

    result = await UserRepository(db_session).patch_user(_patch(user.id, **{field: value}))

    row = (
        await db_session.execute(
            select(User.name, User.email, User.password_hash).where(User.id == user.id)
        )
    ).one()
    assert isinstance(result, UserOutput)
    assert tuple(row) == (expected["name"], expected["email"], expected["new_password_hash"])


async def test_patch_user_normalizes_email(db_session: AsyncSession, user: User) -> None:
    """Email is trimmed and lower-cased.

    Email обрезается и приводится к нижнему регистру.
    """
    result = await UserRepository(db_session).patch_user(
        _patch(user.id, email="  New.Mail@Example.COM ")
    )

    assert result is not None
    assert result.email == "new.mail@example.com"


async def test_patch_user_empty_patch_changes_nothing(db_session: AsyncSession, user: User) -> None:
    """All fields None -> DTO of the unchanged user.

    Все поля None -> DTO без изменений.
    """
    before = (user.name, user.email)

    result = await UserRepository(db_session).patch_user(_patch(user.id))

    assert result is not None
    assert (result.name, result.email) == before


async def test_patch_user_unknown_returns_none(db_session: AsyncSession) -> None:
    """Unknown id -> None.

    Неизвестный id -> None.
    """
    assert await UserRepository(db_session).patch_user(_patch(uuid4(), name="X")) is None


async def test_patch_user_soft_deleted_returns_none(db_session: AsyncSession, make_user) -> None:
    """Soft-deleted user cannot be patched.

    Мягко удалённого пользователя изменить нельзя.
    """
    deleted = await make_user(email="gone@example.com", deleted_at=datetime.now(UTC))

    assert await UserRepository(db_session).patch_user(_patch(deleted.id, name="X")) is None


async def test_patch_user_duplicate_email_raises(
    db_session: AsyncSession, users: list[User]
) -> None:
    """Email taken by another user (any case) -> IntegrityError.

    Email другого пользователя (в любом регистре) -> IntegrityError.
    """
    with pytest.raises(IntegrityError):
        await UserRepository(db_session).patch_user(
            _patch(users[1].id, email=users[0].email.upper())
        )


async def test_patch_user_children_count_skips_deleted(
    db_session: AsyncSession, user: User, make_user
) -> None:
    """children_count in the result counts only live children.

    children_count в результате считает только живых детей.
    """
    await make_user(email="alive@example.com", parent_id=user.id)
    await make_user(email="gone@example.com", parent_id=user.id, deleted_at=datetime.now(UTC))

    result = await UserRepository(db_session).patch_user(_patch(user.id, name="Новое"))

    assert result is not None
    assert result.children_count == 1
