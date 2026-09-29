import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Permission, PermissionAction, PermissionResource, PermissionZone


@pytest_asyncio.fixture
async def permissions(
    db_session: AsyncSession,
) -> list[Permission]:
    SELECTED_RES = [
        {"name": "юзеров", "item": PermissionResource.USERS},
        {"name": "ролей", "item": PermissionResource.ROLES},
        {"name": "товаров", "item": PermissionResource.PRODUCTS},
    ]
    SELECTED_ACT = [
        {
            "name": "добавление ",
            "item": PermissionAction.CREATE,
        },
        {"name": "чтение ", "item": PermissionAction.READ},
        {"name": "обновление ", "item": PermissionAction.UPDATE},
        {"name": "удаление", "item": PermissionAction.DELETE},
    ]
    permissions = []
    for res in SELECTED_RES:
        for act in SELECTED_ACT:
            zone = (
                PermissionZone.ADMIN
                if res["item"] == PermissionResource.PRODUCTS
                else PermissionZone.PUBLIC
            )
            new = Permission(
                name=act["name"] + res["name"],
                description="Право на " + act["name"] + res["name"],
                resource=res["item"],
                action=act["item"],
                zone=zone,
            )
            permissions.append(new)
            db_session.add(new)
    await db_session.flush()
    return permissions


# @pytest_asyncio.fixture
# async def user_permissions(
#     db_session: AsyncSession,
# ) -> list[Permission]:
#     SELECTED_RES = [
#         {"name": "юзеров", "item": PermissionResource.USERS},
#         {"name": "ролей", "item": PermissionResource.ROLES},
#         {"name": "товаров", "item": PermissionResource.PRODUCTS},
#     ]
#     SELECTED_ACT = [
#         {
#             "name": "архивирование ",
#             "item": PermissionAction.ARCHIVE,
#         },
#     ]
#     permissions = []
#     for res in SELECTED_RES:
#         for act in SELECTED_ACT:
#             new = Permission(
#                 name=act["name"] + res["name"],
#                 description="Право на " + act["name"] + res["name"],
#                 resource=res["item"],
#                 action=act["item"],
#                 is_system=False,
#             )
#             permissions.append(new)
#             db_session.add(new)
#     await db_session.flush()
#     return permissions


@pytest_asyncio.fixture
async def make_permission(db_session: AsyncSession):
    async def _make(
        *,
        resource: PermissionResource,
        action: PermissionAction,
        name: str | None = None,
        description: str | None = None,
        zone: PermissionZone = PermissionZone.PUBLIC,
    ) -> Permission:
        permission = Permission(
            name=name or f"{action.value} {resource.value}",
            description=description,
            resource=resource,
            action=action,
            zone=zone,
        )
        db_session.add(permission)
        await db_session.flush()
        return permission

    return _make
