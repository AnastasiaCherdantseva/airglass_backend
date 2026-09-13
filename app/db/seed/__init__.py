"""
Загрузка seed-данных.
"""
from app.core.security import hash_password

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import (
    Role,
    Permission,
    PermissionResource,
    PermissionAction,
    PermissionScope, User, UserRole, RolePermission
)
from app.models.media import MediaType
from app.models.projects import ProjectStatus
from app.models.catalog import (
    Unit,
    Color,
    Material,
    Category,
    VisualType,
    ColorGroup,
    ColorVisualType,
    MaterialGroup,
)
from app.models.templates import GalleryRuleCondition, GalleryRule, BindingType
from app.models.attributes import Attribute, AttributeDataType, AttributeOption
from app.models.usage import UsageRole

from app.db.seed.roles import ROLES
from app.db.seed.categories import CATEGORIES
from app.db.seed.visual_types import VISUAL_TYPES
from app.db.seed.permissions import PERMISSIONS
from app.db.seed.media_types import MEDIA_TYPES
from app.db.seed.project_statuses import PROJECT_STATUSES
from app.db.seed.units import UNITS
from app.db.seed.materials import MATERIALS
from app.db.seed.gallery_rules import GALLERY_RULES
from app.db.seed.color_groups import COLOR_GROUPS
from app.db.seed.material_groups import MATERIAL_GROUPS
from app.db.seed.colors import ALL_COLORS
from app.db.seed.color_visual_types import COLOR_VISUAL_TYPES
from app.db.seed.binding_types import BINDING_TYPES
from app.db.seed.attributes import ATTRIBUTES
from app.db.seed.attribute_options import ATTRIBUTE_OPTIONS
from app.db.seed.users import SEED_ADMIN
from app.db.seed.role_permissions import ROLE_PERMISSIONS
from app.db.seed.usage_roles import USAGE_ROLES


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
    await _seed_gallery_rules(db, categories)
    await _seed_admin_user(db, roles)



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
    result = await db.execute(
        select(ColorVisualType.color_id, ColorVisualType.visual_type_id)
    )
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

async def _seed_roles(db: AsyncSession) -> dict[str, Role]:
    """Загрузить роли. Возвращает {code: Role}."""
    result = await db.execute(select(Role))
    existing = {r.code: r for r in result.scalars().all()}

    to_create = [r for r in ROLES if r["code"] not in existing]

    for item in to_create:
        obj = Role(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            is_system=item.get("is_system", False),
            is_active=item.get("is_active", True),
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Роли: добавлено {len(to_create)}")
    else:
        print("   • Роли: уже загружены")

    return existing


async def _seed_permissions(db: AsyncSession) -> dict[str, Permission]:
    """Загрузить права. Возвращает {code: Permission}."""
    result = await db.execute(select(Permission))
    existing = {p.code: p for p in result.scalars().all()}

    to_create = [p for p in PERMISSIONS if p["code"] not in existing]

    for item in to_create:
        obj = Permission(
            code=item["code"],
            name=item["name"],
            description=item.get("description"),
            resource=PermissionResource(item["resource"]),
            action=PermissionAction(item["action"]),
            scope=PermissionScope(item["scope"]),
            is_active=item.get("is_active", True),
            is_system=item.get("is_system", True),  # права из сида — системные
        )
        db.add(obj)
        existing[item["code"]] = obj

    if to_create:
        await db.flush()
        print(f"   • Права: добавлено {len(to_create)}")
    else:
        print("   • Права: уже загружены")

    return existing


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
    result = await db.execute(
        select(AttributeOption.attribute_id, AttributeOption.code)
    )
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

async def _seed_admin_user(
    db: AsyncSession,
    roles: dict[str, Role],
) -> User | None:
    """Создать пользователя-администратора (идемпотентно по email)."""
    email = SEED_ADMIN["email"]

    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()

    if existing is not None:
        print("   • Пользователь-администратор: уже существует")
        return existing

    role = roles.get(SEED_ADMIN["role_code"])
    if role is None:
        print(f"   ⚠️  Роль '{SEED_ADMIN['role_code']}' не найдена — пользователь не создан")
        return None

    user = User(
        name=SEED_ADMIN["name"],
        email=email,
        password_hash=hash_password(SEED_ADMIN["password"]),
        is_active=SEED_ADMIN.get("is_active", True),
    )
    db.add(user)
    await db.flush()  # чтобы получить user.id

    db.add(UserRole(user_id=user.id, role_id=role.id))
    await db.flush()

    print(f"   • Пользователь-администратор: создан ({email})")
    return user


async def _seed_role_permissions(
    db: AsyncSession,
    roles: dict[str, Role],
    permissions: dict[str, Permission],
) -> None:
    """Загрузить связи ролей с правами (идемпотентно)."""
    # Существующие связи: {(role_id, permission_id)}
    result = await db.execute(
        select(RolePermission.role_id, RolePermission.permission_id)
    )
    existing_links = {(row[0], row[1]) for row in result.all()}

    all_permission_ids = [p.id for p in permissions.values()]

    added = 0
    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        role = roles.get(role_code)
        if role is None:
            print(f"   ⚠️  Роль '{role_code}' не найдена для связей с правами")
            continue

        # "*" = все права
        if permission_codes == ["*"]:
            target_permission_ids = all_permission_ids
        else:
            target_permission_ids = []
            for perm_code in permission_codes:
                perm = permissions.get(perm_code)
                if perm is None:
                    print(f"   ⚠️  Право '{perm_code}' не найдено для роли '{role_code}'")
                    continue
                target_permission_ids.append(perm.id)

        for perm_id in target_permission_ids:
            key = (role.id, perm_id)
            if key in existing_links:
                continue

            db.add(RolePermission(role_id=role.id, permission_id=perm_id))
            existing_links.add(key)
            added += 1

    if added:
        await db.flush()
        print(f"   • Связи роль↔право: добавлено {added}")
    else:
        print("   • Связи роль↔право: уже загружены")



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