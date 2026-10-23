"""
Загрузка seed-данных.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.seed.attribute_options import ATTRIBUTE_OPTIONS
from app.db.seed.attributes import ATTRIBUTES
from app.db.seed.binding_types import BINDING_TYPES
from app.db.seed.categories import CATEGORIES
from app.db.seed.category_color_groups import CATEGORY_COLOR_GROUPS
from app.db.seed.category_material_groups import CATEGORY_MATERIAL_GROUPS
from app.db.seed.color_groups import COLOR_GROUPS
from app.db.seed.color_visual_types import COLOR_VISUAL_TYPES
from app.db.seed.colors import ALL_COLORS
from app.db.seed.gallery_rules import GALLERY_RULES
from app.db.seed.material_groups import MATERIAL_GROUPS
from app.db.seed.materials import MATERIALS
from app.db.seed.media_types import MEDIA_TYPES
from app.db.seed.permissions import PERMISSIONS, ZONE_BY_RESOURCE
from app.db.seed.project_statuses import PROJECT_STATUSES
from app.db.seed.roles import ROLES
from app.db.seed.units import UNITS
from app.db.seed.usage_roles import USAGE_ROLES
from app.db.seed.users import SEED_ADMIN
from app.db.seed.visual_types import VISUAL_TYPES
from app.models.attributes import Attribute, AttributeDataType, AttributeOption
from app.models.catalog import (
    Category,
    Color,
    ColorGroup,
    ColorVisualType,
    Material,
    MaterialGroup,
    Unit,
    VisualType,
)
from app.models.catalog.category_color_group import CategoryColorGroup
from app.models.catalog.category_material_group import CategoryMaterialGroup
from app.models.media import MediaType
from app.models.projects import ProjectStatus
from app.models.system import (
    Permission,
    PermissionAction,
    PermissionResource,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.models.system.permission import PermissionZone
from app.models.system.permission_condition import (
    ConditionType,
    PermissionCondition,
    PermissionEffect,
)
from app.models.templates import BindingType, GalleryRule, GalleryRuleCondition
from app.models.usage import UsageRole
from app.repositories.system.role_permission import RolePermissionRepository
from app.repositories.system.user_direct_permission import UserDirectPermissionRepository
from app.repositories.system.user_permission import UserPermissionRepository
from app.repositories.system.user_role import UserRoleRepository
from app.services.sync_user_permissions import sync_user_permissions

logger = logging.getLogger(__name__)

# ============================================================
# ТОЧКА ВХОДА
# ============================================================


async def seed_all(db: AsyncSession) -> None:
    """Загрузить все seed-данные."""
    print("🌱 Загрузка seed-данных...")

    # 1. Независимые справочники
    roles = await _seed_roles(db)
    permissions = await _seed_permissions(db)
    await _seed_role_permissions(db, roles, permissions)
    await _seed_project_statuses(db)
    await _seed_media_types(db)
    await _seed_binding_types(db)
    await _seed_usage_roles(db)

    # 2. Единицы измерения (нужны для атрибутов)
    units = await _seed_units(db)

    # 3. Атрибуты + их значения
    attributes = await _seed_attributes(db, units)
    await _seed_attribute_options(db, attributes)

    # 4. Цвета (группы → типы визуализации → цвета → связи)
    color_groups = await _seed_color_groups(db)
    visual_types = await _seed_visual_types(db)
    colors = await _seed_colors(db, color_groups)
    await _seed_color_visual_types(db, colors, visual_types)

    # 5. Материалы (группы → материалы)
    material_groups = await _seed_material_groups(db)
    await _seed_materials(db, material_groups)

    # 6. Категории и правила галереи (зависят от категорий)
    categories = await _seed_categories(db)
    await _seed_category_color_groups(db, categories, color_groups)
    await _seed_category_material_groups(db, categories, material_groups)
    await _seed_gallery_rules(db, categories)

    # 7. Админ + материализация его прав (user_permissions)
    admin = await _seed_admin_user(db, roles["SYSTEM_ADMIN"])
    await _sync_admin_permissions(db, admin.id)

    await db.commit()
    print("✅ Seed-данные загружены!")


# ============================================================
# СПРАВОЧНИКИ
# ============================================================


async def _seed_units(db: AsyncSession) -> dict[str, Unit]:
    """Загрузить единицы измерения. Возвращает {code: Unit}."""
    result = await db.execute(select(Unit))
    existing = {u.code: u for u in result.scalars().all()}

    to_create = [u for u in UNITS if u["code"] not in existing]

    for item in to_create:
        obj = Unit(
            code=item["code"],
            name=item["name"],
            symbol=item["symbol"],
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Единицы измерения: добавлено {len(to_create)}")
    else:
        print("   • Единицы измерения: уже загружены")

    return existing


async def _seed_material_groups(db: AsyncSession) -> dict[str, MaterialGroup]:
    """Загрузить группы материалов. Возвращает {code: MaterialGroup}."""
    result = await db.execute(select(MaterialGroup))
    existing = {g.code: g for g in result.scalars().all()}

    to_create = [g for g in MATERIAL_GROUPS if g["code"] not in existing]

    for item in to_create:
        obj = MaterialGroup(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Группы материалов: добавлено {len(to_create)}")
    else:
        print("   • Группы материалов: уже загружены")

    return existing


async def _seed_materials(
    db: AsyncSession,
    material_groups: dict[str, MaterialGroup],
) -> dict[str, Material]:
    """Загрузить материалы. Возвращает {code: Material}."""
    result = await db.execute(select(Material))
    existing = {m.code: m for m in result.scalars().all()}

    to_create = [m for m in MATERIALS if m["code"] not in existing]

    for item in to_create:
        group = material_groups.get(item["group_code"])
        if group is None:
            print(f"   ⚠️  Группа '{item['group_code']}' не найдена для материала '{item['code']}'")
            continue

        obj = Material(
            code=item["code"],
            name=item["name"],
            description=item.get("description") or None,
            group_id=group.id,
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Материалы: добавлено {len(to_create)}")
    else:
        print("   • Материалы: уже загружены")

    return existing


async def _seed_color_groups(db: AsyncSession) -> dict[str, ColorGroup]:
    """Загрузить группы цветов. Возвращает {code: ColorGroup}."""
    result = await db.execute(select(ColorGroup))
    existing = {g.code: g for g in result.scalars().all()}

    to_create = [g for g in COLOR_GROUPS if g["code"] not in existing]

    for item in to_create:
        obj = ColorGroup(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Группы цветов: добавлено {len(to_create)}")
    else:
        print("   • Группы цветов: уже загружены")

    return existing


async def _seed_visual_types(db: AsyncSession) -> dict[str, VisualType]:
    """Загрузить типы визуализации. Возвращает {code: VisualType}."""
    result = await db.execute(select(VisualType))
    existing = {v.code: v for v in result.scalars().all()}

    to_create = [v for v in VISUAL_TYPES if v["code"] not in existing]

    for item in to_create:
        obj = VisualType(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Типы визуализации: добавлено {len(to_create)}")
    else:
        print("   • Типы визуализации: уже загружены")

    return existing


async def _seed_colors(
    db: AsyncSession,
    groups: dict[str, ColorGroup],
) -> dict[str, Color]:
    """Загрузить цвета. Возвращает {code: Color}."""
    result = await db.execute(select(Color))
    existing = {c.code: c for c in result.scalars().all()}

    to_create = [c for c in ALL_COLORS if c["code"] not in existing]

    for item in to_create:
        group = groups.get(item["group_code"])
        if group is None:
            print(f"   ⚠️  Группа '{item['group_code']}' не найдена для цвета '{item['code']}'")
            continue

        obj = Color(
            code=item["code"],
            name=item["name"],
            hex_color=item.get("hex_color"),
            group_id=group.id,
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Цвета: добавлено {len(to_create)}")
    else:
        print("   • Цвета: уже загружены")

    return existing


async def _seed_color_visual_types(
    db: AsyncSession,
    colors: dict[str, Color],
    visual_types: dict[str, VisualType],
) -> None:
    """Загрузить связи цветов с типами визуализации."""
    result = await db.execute(select(ColorVisualType.color_id, ColorVisualType.visual_type_id))
    existing_links = {(row[0], row[1]) for row in result.all()}

    added = 0
    for color_code, vt_codes in COLOR_VISUAL_TYPES.items():
        color = colors.get(color_code)
        if color is None:
            print(f"   ⚠️  Цвет '{color_code}' не найден для связи с visual_types")
            continue

        for vt_code in vt_codes:
            vt = visual_types.get(vt_code)
            if vt is None:
                print(f"   ⚠️  Тип визуализации '{vt_code}' не найден")
                continue

            key = (color.id, vt.id)
            if key in existing_links:
                continue

            db.add(ColorVisualType(color_id=color.id, visual_type_id=vt.id))
            existing_links.add(key)
            added += 1

    if added:
        await db.flush()
        print(f"   • Связи цвет↔визуализация: добавлено {added}")
    else:
        print("   • Связи цвет↔визуализация: уже загружены")


async def _seed_categories(db: AsyncSession) -> dict[str, Category]:
    """Загрузить дерево категорий (идемпотентно). Возвращает {code: Category}."""
    result = await db.execute(select(Category))
    existing = {c.code: c for c in result.scalars().all()}

    to_create = [c for c in CATEGORIES if c["code"] not in existing]

    if not to_create:
        print("   • Категории: уже загружены")
        return existing

    # Первый проход: создаём без родителей
    for item in to_create:
        obj = Category(
            code=item["code"],
            name=item["name"],
            sort_order=item.get("sort_order", 0),
            parent_id=None,
        )
        db.add(obj)
        existing[item["code"]] = obj

    await db.flush()

    # Второй проход: проставляем родителей
    for item in to_create:
        parent_code = item.get("parent_code")
        if not parent_code:
            continue

        parent = existing.get(parent_code)
        if parent is None:
            print(f"   ⚠️  Родитель '{parent_code}' не найден для '{item['code']}'")
            continue

        existing[item["code"]].parent_id = parent.id

    await db.flush()
    print(f"   • Категории: добавлено {len(to_create)}")

    return existing


# ============================================================
# СИСТЕМА
# ============================================================


async def _seed_roles(session: AsyncSession) -> dict[str, Role]:
    """
    Создать системные роли (идемпотентно).

    Args:
        session: AsyncSession.

    Returns:
        Словарь {code: Role} — для использования в других сидерах.
    """
    result_map: dict[str, Role] = {}

    for role_seed in ROLES:
        stmt = select(Role).where(
            Role.name == role_seed["name"],
            Role.owner_id.is_(None),  # системная роль
        )
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()

        if role is None:
            role = Role(
                owner_id=None,  # системная роль
                name=role_seed["name"],
                description=role_seed["description"],
                is_system=role_seed["is_system"],
                is_active=role_seed["is_active"],
            )
            session.add(role)
            await session.flush()
            logger.info("Created system role: %s", role_seed["name"])
        else:
            logger.info("System role already exists: %s", role_seed["name"])

        result_map[role_seed["code"]] = role

    return result_map


async def _seed_permissions(
    session: AsyncSession,
) -> dict[str, list[PermissionCondition]]:
    """
    Create permissions and their conditions (idempotent).

    A permission is looked up by (resource, action), because ``code`` is a
    DB-computed column (``USERS.CREATE``).

    Returns:
        ``{"USERS.CREATE": [PermissionCondition, ...]}``.

    Создать права и их варианты (идемпотентно).

    Право ищется по (resource, action), так как ``code`` — вычисляемая
    колонка БД (``USERS.CREATE``).

    Returns:
        ``{"USERS.CREATE": [PermissionCondition, ...]}``.
    """
    result_map: dict[str, list[PermissionCondition]] = {}

    for perm_seed in PERMISSIONS:
        resource = PermissionResource(perm_seed["resource"])
        action = PermissionAction(perm_seed["action"])

        stmt = select(Permission).where(
            Permission.resource == resource,
            Permission.action == action,
        )
        permission = (await session.execute(stmt)).scalar_one_or_none()

        if permission is None:
            permission = Permission(
                name=perm_seed["name"],
                resource=resource,
                action=action,
                zone=PermissionZone(ZONE_BY_RESOURCE[perm_seed["resource"]]),
            )
            session.add(permission)
            await session.flush()

        conditions: list[PermissionCondition] = []
        for cond_seed in perm_seed["conditions"]:
            cond_type = ConditionType(cond_seed["type"])
            cond_effect = PermissionEffect(cond_seed["effect"])

            stmt = select(PermissionCondition).where(
                PermissionCondition.permission_id == permission.id,
                PermissionCondition.type == cond_type,
                PermissionCondition.effect == cond_effect,
            )
            condition = (await session.execute(stmt)).scalar_one_or_none()

            if condition is None:
                condition = PermissionCondition(
                    permission_id=permission.id,
                    type=cond_type,
                    effect=cond_effect,
                    is_active=True,
                )
                session.add(condition)
                await session.flush()

            conditions.append(condition)

        result_map[f"{resource.name}.{action.name}"] = conditions

    return result_map


async def _seed_category_color_groups(
    db: AsyncSession,
    categories: dict[str, Category],
    color_groups: dict[str, ColorGroup],
) -> None:
    """
    Link categories to available color groups (idempotent).

    Связать категории с доступными группами цветов (идемпотентно).
    """
    result = await db.execute(
        select(CategoryColorGroup.category_id, CategoryColorGroup.color_group_id)
    )
    existing = {(row[0], row[1]) for row in result.all()}

    added = 0
    for item in CATEGORY_COLOR_GROUPS:
        category = categories.get(item["category_code"])
        group = color_groups.get(item["color_group_code"])
        if category is None or group is None:
            print(f"   ⚠️  Не найдена пара '{item['category_code']}' / '{item['color_group_code']}'")
            continue

        key = (category.id, group.id)
        if key in existing:
            continue

        db.add(CategoryColorGroup(category_id=category.id, color_group_id=group.id))
        existing.add(key)
        added += 1

    if added:
        await db.flush()
        print(f"   • Связи категория↔группа цветов: добавлено {added}")
    else:
        print("   • Связи категория↔группа цветов: уже загружены")


async def _seed_category_material_groups(
    db: AsyncSession,
    categories: dict[str, Category],
    material_groups: dict[str, MaterialGroup],
) -> None:
    """
    Link categories to available material groups (idempotent).

    Связать категории с доступными группами материалов (идемпотентно).
    """
    result = await db.execute(
        select(CategoryMaterialGroup.category_id, CategoryMaterialGroup.material_group_id)
    )
    existing = {(row[0], row[1]) for row in result.all()}

    added = 0
    for item in CATEGORY_MATERIAL_GROUPS:
        category = categories.get(item["category_code"])
        group = material_groups.get(item["material_group_code"])
        if category is None or group is None:
            print(
                f"   ⚠️  Не найдена пара '{item['category_code']}' / '{item['material_group_code']}'"
            )
            continue

        key = (category.id, group.id)
        if key in existing:
            continue

        db.add(CategoryMaterialGroup(category_id=category.id, material_group_id=group.id))
        existing.add(key)
        added += 1

    if added:
        await db.flush()
        print(f"   • Связи категория↔группа материалов: добавлено {added}")
    else:
        print("   • Связи категория↔группа материалов: уже загружены")


async def _seed_media_types(db: AsyncSession) -> dict[str, MediaType]:
    """Загрузить типы медиа. Возвращает {code: MediaType}."""
    result = await db.execute(select(MediaType))
    existing = {m.code: m for m in result.scalars().all()}

    to_create = [m for m in MEDIA_TYPES if m["code"] not in existing]

    for item in to_create:
        obj = MediaType(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            is_system=item.get("is_system", False),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Типы медиа: добавлено {len(to_create)}")
    else:
        print("   • Типы медиа: уже загружены")

    return existing


async def _seed_project_statuses(db: AsyncSession) -> dict[str, ProjectStatus]:
    """Загрузить статусы проектов. Возвращает {code: ProjectStatus}."""
    result = await db.execute(select(ProjectStatus))
    existing = {s.code: s for s in result.scalars().all()}

    to_create = [s for s in PROJECT_STATUSES if s["code"] not in existing]

    for item in to_create:
        obj = ProjectStatus(
            code=item["code"],
            name=item["name"],
            sort_order=item.get("sort_order", 0),
            is_final=item.get("is_final", False),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Статусы проектов: добавлено {len(to_create)}")
    else:
        print("   • Статусы проектов: уже загружены")

    return existing


async def _seed_admin_user(session: AsyncSession, admin_role: Role) -> User:
    """
    Create the admin user and assign the role (idempotent).

    Email is matched via ``lower(email)`` among non-deleted users (ADR-USER-002).

    Args:
        session: AsyncSession.
        admin_role: System administrator role.

    Returns:
        The admin ``User``.

    Создать администратора и назначить роль (идемпотентно).

    Email ищется по ``lower(email)`` среди неудалённых (ADR-USER-002).

    Args:
        session: AsyncSession.
        admin_role: Системная роль администратора.

    Returns:
        Пользователь-администратор ``User``.
    """
    email = SEED_ADMIN["email"].strip().lower()

    stmt = select(User).where(func.lower(User.email) == email, User.deleted_at.is_(None))
    user = (await session.execute(stmt)).scalar_one_or_none()

    if user is None:
        user = User(
            name=SEED_ADMIN["name"],
            email=email,
            password_hash=hash_password(SEED_ADMIN["password"]),
            is_active=SEED_ADMIN["is_active"],
            email_verified=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()
        logger.info("Created admin user: %s", email)
    else:
        logger.info("Admin user already exists: %s", email)

    stmt = select(UserRole).where(
        UserRole.user_id == user.id,
        UserRole.role_id == admin_role.id,
    )
    if (await session.execute(stmt)).scalar_one_or_none() is None:
        session.add(UserRole(user_id=user.id, role_id=admin_role.id))
        logger.info("Assigned role %s to %s", admin_role.name, email)
    await session.flush()

    return user


async def _sync_admin_permissions(session: AsyncSession, user_id: UUID) -> None:
    """
    Materialize the user's permissions into ``user_permissions`` (idempotent).

    Authorization reads only ``user_permissions`` (ADR-ACCESS-005), so without
    this step the seeded admin has no rights.

    Материализовать права пользователя в ``user_permissions`` (идемпотентно).

    Авторизация читает только ``user_permissions`` (ADR-ACCESS-005), поэтому
    без этого шага у засидированного админа нет прав.
    """
    await sync_user_permissions(
        user_id,
        user_roles=UserRoleRepository(session),
        role_permissions=RolePermissionRepository(session),
        user_direct_permissions=UserDirectPermissionRepository(session),
        user_permissions=UserPermissionRepository(session),
    )


async def _seed_role_permissions(
    session: AsyncSession,
    roles: dict[str, Role],
    conditions: dict[str, list[PermissionCondition]],
) -> None:
    """Создать связи роль ↔ условие (идемпотентно)."""
    result = await session.execute(select(RolePermission.role_id, RolePermission.condition_id))
    existing = {(row[0], row[1]) for row in result.all()}

    admin_role = roles.get("SYSTEM_ADMIN")
    if admin_role is None:
        print("   ⚠️  Роль SYSTEM_ADMIN не найдена")
        return

    added = 0
    for perm_code, perm_conditions in conditions.items():
        for cond in perm_conditions:
            if cond.type != ConditionType.ALL:
                continue
            if cond.effect != PermissionEffect.ALLOW:
                continue

            key = (admin_role.id, cond.id)
            if key in existing:
                continue

            session.add(
                RolePermission(
                    role_id=admin_role.id,
                    condition_id=cond.id,
                )
            )
            existing.add(key)
            added += 1

    if added:
        await session.flush()
        print(f"   • Связи SYSTEM_ADMIN ↔ условия: добавлено {added}")
    else:
        print("   • Связи SYSTEM_ADMIN ↔ условия: уже загружены")


# ============================================================
# ШАБЛОНЫ
# ============================================================


async def _seed_binding_types(db: AsyncSession) -> dict[str, BindingType]:
    """Загрузить типы обвязки. Возвращает {code: BindingType}."""
    result = await db.execute(select(BindingType))
    existing = {b.code: b for b in result.scalars().all()}

    to_create = [b for b in BINDING_TYPES if b["code"] not in existing]

    for item in to_create:
        obj = BindingType(
            code=item["code"],
            name=item["name"],
            description=item.get("description") or None,
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Типы обвязки: добавлено {len(to_create)}")
    else:
        print("   • Типы обвязки: уже загружены")

    return existing


async def _seed_gallery_rules(
    db: AsyncSession,
    categories: dict[str, Category],
) -> dict[str, GalleryRule]:
    """Загрузить глобальные правила галереи. Возвращает {code: GalleryRule}."""
    result = await db.execute(select(GalleryRule))
    existing = {r.code: r for r in result.scalars().all()}

    to_create = [r for r in GALLERY_RULES if r["code"] not in existing]

    for item in to_create:
        rule = GalleryRule(
            code=item["code"],
            name=item["name"],
            description=item.get("description") or None,
            sort_order=item.get("sort_order", 0),
            is_active=item.get("is_active", True),
        )
        db.add(rule)
        existing[item["code"]] = rule

        for idx, cond in enumerate(item.get("conditions", []), start=1):
            category_code = cond.get("category_code")
            category = categories.get(category_code) if category_code else None

            if category_code and category is None:
                print(f"   ⚠️  Категория '{category_code}' не найдена для правила '{item['code']}'")
                continue

            db.add(
                GalleryRuleCondition(
                    rule=rule,
                    category_id=category.id if category else None,
                    sort_order=cond.get("sort_order", idx),
                )
            )

    if to_create:
        await db.flush()
        print(f"   • Правила галереи: добавлено {len(to_create)}")
    else:
        print("   • Правила галереи: уже загружены")

    return existing


# ============================================================
# АТРИБУТЫ
# ============================================================


async def _seed_attributes(
    db: AsyncSession,
    units: dict[str, Unit],
) -> dict[str, Attribute]:
    """Загрузить атрибуты. Возвращает {code: Attribute}."""
    result = await db.execute(select(Attribute))
    existing = {a.code: a for a in result.scalars().all()}

    to_create = [a for a in ATTRIBUTES if a["code"] not in existing]

    for item in to_create:
        unit_code = item.get("unit_code")
        unit = units.get(unit_code) if unit_code else None

        if unit_code and unit is None:
            print(f"   ⚠️  Единица измерения '{unit_code}' не найдена для атрибута '{item['code']}'")
            continue

        obj = Attribute(
            code=item["code"],
            name=item["name"],
            data_type=AttributeDataType(item["data_type"]),
            unit_id=unit.id if unit else None,
            is_filterable=item.get("is_filterable", False),
            is_required=item.get("is_required", False),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Атрибуты: добавлено {len(to_create)}")
    else:
        print("   • Атрибуты: уже загружены")

    return existing


async def _seed_attribute_options(
    db: AsyncSession,
    attributes: dict[str, Attribute],
) -> None:
    """Загрузить значения атрибутов (OPTION)."""
    result = await db.execute(select(AttributeOption.attribute_id, AttributeOption.code))
    existing = {(row[0], row[1]) for row in result.all()}

    added = 0
    for attr_code, options in ATTRIBUTE_OPTIONS.items():
        attribute = attributes.get(attr_code)
        if attribute is None:
            print(f"   ⚠️  Атрибут '{attr_code}' не найден для значений")
            continue

        for item in options:
            key = (attribute.id, item["code"])
            if key in existing:
                continue

            db.add(
                AttributeOption(
                    attribute_id=attribute.id,
                    value=item["value"],
                    code=item["code"],
                    sort_order=item.get("sort_order", 0),
                    is_active=item.get("is_active", True),
                )
            )
            existing.add(key)
            added += 1

    if added:
        await db.flush()
        print(f"   • Значения атрибутов: добавлено {added}")
    else:
        print("   • Значения атрибутов: уже загружены")


async def _seed_usage_roles(db: AsyncSession) -> dict[str, UsageRole]:
    """Загрузить роли использования. Возвращает {code: UsageRole}."""
    result = await db.execute(select(UsageRole))
    existing = {u.code: u for u in result.scalars().all()}

    to_create = [u for u in USAGE_ROLES if u["code"] not in existing]

    for item in to_create:
        obj = UsageRole(
            code=item["code"],
            name=item["name"],
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Роли использования: добавлено {len(to_create)}")
    else:
        print("   • Роли использования: уже загружены")

    return existing
