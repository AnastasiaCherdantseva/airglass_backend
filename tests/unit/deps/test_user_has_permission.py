"""Unit-тесты user_has_permission."""

from uuid import uuid4

from app.core.security import user_has_permission
from app.dto import CurrentUser, GroupedPermission
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.models.system.permission_condition import ConditionType, PermissionEffect


def make_condition(
    *,
    effect: PermissionEffect = PermissionEffect.ALLOW,
    condition_type: ConditionType = ConditionType.ALL,
    is_active: bool = True,
) -> PermissionConditionAllOutPut:
    """Создать condition для тестов."""
    return PermissionConditionAllOutPut(
        id=uuid4(),
        permission_id=uuid4(),
        category_id=None,
        role_id=None,
        media_type_id=None,
        effect=effect,
        type=condition_type,
        is_active=is_active,
    )


def make_grouped(
    code: str,
    conditions: list[PermissionConditionAllOutPut],
) -> GroupedPermission:
    """Создать GroupedPermission для тестов."""
    return GroupedPermission(
        id=uuid4(),
        code=code,
        conditions=conditions,
    )


def make_current_user(
    permissions: list[GroupedPermission] | None = None,
) -> CurrentUser:
    """Создать CurrentUser для тестов."""
    return CurrentUser(
        id=uuid4(),
        email="test@example.com",
        name="Test",
        is_active=True,
        parent_id=None,
        permissions=permissions or [],
        has_admin_access=False,
        children_count=0,
    )


# ─────────────────────────────────────────────────────────────
# grouped не найден
# ─────────────────────────────────────────────────────────────


def test_no_permissions_at_all() -> None:
    """Пустой список прав → False."""
    user = make_current_user(permissions=[])

    assert user_has_permission(user, "users.read") is False


def test_code_not_found() -> None:
    """Права с нужным code нет → False."""
    user = make_current_user(permissions=[make_grouped("users.create", [make_condition()])])

    assert user_has_permission(user, "users.read") is False


# ─────────────────────────────────────────────────────────────
# ALLOW
# ─────────────────────────────────────────────────────────────


def test_single_allow_active() -> None:
    """Одно активное ALLOW → True."""
    user = make_current_user(
        permissions=[make_grouped("users.read", [make_condition(effect=PermissionEffect.ALLOW)])]
    )

    assert user_has_permission(user, "users.read") is True


def test_single_allow_inactive() -> None:
    """Одно неактивное ALLOW → False."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [make_condition(effect=PermissionEffect.ALLOW, is_active=False)],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


def test_multiple_allow() -> None:
    """Несколько ALLOW → True."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.ALLOW),
                    make_condition(effect=PermissionEffect.ALLOW),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is True


# ─────────────────────────────────────────────────────────────
# DENY
# ─────────────────────────────────────────────────────────────


def test_single_deny_active() -> None:
    """Одно активное DENY → False."""
    user = make_current_user(
        permissions=[make_grouped("users.read", [make_condition(effect=PermissionEffect.DENY)])]
    )

    assert user_has_permission(user, "users.read") is False


def test_single_deny_inactive() -> None:
    """Одно неактивное DENY, без ALLOW → False."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [make_condition(effect=PermissionEffect.DENY, is_active=False)],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


# ─────────────────────────────────────────────────────────────
# ALLOW + DENY
# ─────────────────────────────────────────────────────────────


def test_allow_and_deny_active() -> None:
    """ALLOW + DENY, оба активны → False (DENY приоритетнее)."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.ALLOW),
                    make_condition(effect=PermissionEffect.DENY),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


def test_deny_first_then_allow() -> None:
    """DENY первый, потом ALLOW → False."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.DENY),
                    make_condition(effect=PermissionEffect.ALLOW),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


def test_allow_first_then_deny() -> None:
    """ALLOW первый, потом DENY → False."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.ALLOW),
                    make_condition(effect=PermissionEffect.DENY),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


def test_allow_active_deny_inactive() -> None:
    """ALLOW активен, DENY неактивен → True."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.ALLOW, is_active=True),
                    make_condition(effect=PermissionEffect.DENY, is_active=False),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is True


def test_allow_inactive_deny_inactive() -> None:
    """Оба неактивны → False."""
    user = make_current_user(
        permissions=[
            make_grouped(
                "users.read",
                [
                    make_condition(effect=PermissionEffect.ALLOW, is_active=False),
                    make_condition(effect=PermissionEffect.DENY, is_active=False),
                ],
            )
        ]
    )

    assert user_has_permission(user, "users.read") is False


# ─────────────────────────────────────────────────────────────
# Другие code / conditions
# ─────────────────────────────────────────────────────────────


def test_other_codes_ignored() -> None:
    """Права с другим code не влияют."""
    user = make_current_user(
        permissions=[
            make_grouped("users.read", [make_condition(effect=PermissionEffect.ALLOW)]),
            make_grouped("users.create", [make_condition(effect=PermissionEffect.DENY)]),
        ]
    )

    assert user_has_permission(user, "users.read") is True
    assert user_has_permission(user, "users.create") is False


def test_empty_conditions() -> None:
    """grouped есть, но conditions пусты → False."""
    user = make_current_user(permissions=[make_grouped("users.read", [])])

    assert user_has_permission(user, "users.read") is False
