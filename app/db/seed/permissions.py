from typing import Final, TypedDict


class PermissionConditionSeed(TypedDict):
    """
    Condition variant of a permission (only parameterless types are seeded).

    Вариант права (сидятся только типы без FK: all / creator / subtree).
    """

    type: str
    # effect: str


class PermissionSeed(TypedDict):
    """
    One permission with its condition variants.

    Одно право с его вариантами.
    """

    resource: str
    action: str
    name: str
    conditions: list[PermissionConditionSeed]


ZONE_BY_RESOURCE: Final[dict[str, str]] = {
    "users": "public",
    "roles": "public",
    "projects": "public",
    "customers": "public",
    "calculator": "public",
    "media": "public",
    "products": "admin",
    "categories": "admin",
    "templates": "admin",
    "suppliers": "admin",
    "settings": "admin",
    "audit_log": "admin",
}

ALL: Final[PermissionConditionSeed] = {
    "type": "all",
    # "effect": "allow"
}
CREATOR: Final[PermissionConditionSeed] = {
    "type": "creator",
    #    "effect": "allow"
}
SUBTREE: Final[PermissionConditionSeed] = {
    "type": "subtree",
    #    "effect": "allow"
}
CREATOR: Final[PermissionConditionSeed] = {
    "type": "creator",
    #    "effect": "allow"
}

PERMISSIONS: list[PermissionSeed] = [
    # CALCULATOR
    {
        "resource": "calculator",
        "action": "read",
        "name": "Доступ к калькулятору",
        "conditions": [ALL],
    },
    # USERS
    {
        "resource": "users",
        "action": "create",
        "name": "Создание пользователей",
        "conditions": [],
    },
    {
        "resource": "users",
        "action": "read",
        "name": "Просмотр пользователей",
        "conditions": [SUBTREE],
    },
    {
        "resource": "users",
        "action": "update",
        "name": "Редактирование пользователей",
        "conditions": [SUBTREE],
    },
    {
        "resource": "users",
        "action": "delete",
        "name": "Удаление пользователей",
        "conditions": [SUBTREE],
    },
    # ROLES
    {
        "resource": "roles",
        "action": "create",
        "name": "Создание ролей",
        "conditions": [ALL],
    },
    {"resource": "roles", "action": "read", "name": "Просмотр ролей", "conditions": [ALL, CREATOR]},
    {
        "resource": "roles",
        "action": "update",
        "name": "Редактирование ролей",
        "conditions": [CREATOR],
    },
    {
        "resource": "roles",
        "action": "delete",
        "name": "Удаление ролей",
        "conditions": [CREATOR],
    },
    # PRODUCTS
    {"resource": "products", "action": "create", "name": "Создание товаров", "conditions": [ALL]},
    {"resource": "products", "action": "read", "name": "Просмотр товаров", "conditions": [ALL]},
    {
        "resource": "products",
        "action": "update",
        "name": "Редактирование товаров",
        "conditions": [ALL],
    },
    {"resource": "products", "action": "delete", "name": "Удаление товаров", "conditions": [ALL]},
    {"resource": "products", "action": "archive", "name": "Архивация товаров", "conditions": [ALL]},
    {"resource": "products", "action": "export", "name": "Экспорт товаров", "conditions": [ALL]},
    {"resource": "products", "action": "import", "name": "Импорт товаров", "conditions": [ALL]},
    # CATEGORIES
    {
        "resource": "categories",
        "action": "create",
        "name": "Создание категорий",
        "conditions": [ALL],
    },
    {"resource": "categories", "action": "read", "name": "Просмотр категорий", "conditions": [ALL]},
    {
        "resource": "categories",
        "action": "update",
        "name": "Редактирование категорий",
        "conditions": [ALL],
    },
    {
        "resource": "categories",
        "action": "delete",
        "name": "Удаление категорий",
        "conditions": [ALL],
    },
    # TEMPLATES
    {"resource": "templates", "action": "create", "name": "Создание шаблонов", "conditions": [ALL]},
    {
        "resource": "templates",
        "action": "read",
        "name": "Просмотр шаблонов",
        "conditions": [ALL, CREATOR],
    },
    {
        "resource": "templates",
        "action": "update",
        "name": "Редактирование шаблонов",
        "conditions": [ALL, CREATOR],
    },
    {
        "resource": "templates",
        "action": "delete",
        "name": "Удаление шаблонов",
        "conditions": [ALL, CREATOR],
    },
    # PROJECTS
    {"resource": "projects", "action": "create", "name": "Создание проектов", "conditions": [ALL]},
    {
        "resource": "projects",
        "action": "read",
        "name": "Просмотр проектов",
        "conditions": [ALL, CREATOR],
    },
    {
        "resource": "projects",
        "action": "update",
        "name": "Редактирование проектов",
        "conditions": [ALL, CREATOR],
    },
    {
        "resource": "projects",
        "action": "archive",
        "name": "Архивация проектов",
        "conditions": [ALL],
    },
    # CUSTOMERS
    {
        "resource": "customers",
        "action": "create",
        "name": "Создание заказчиков",
        "conditions": [ALL],
    },
    {
        "resource": "customers",
        "action": "read",
        "name": "Просмотр заказчиков",
        "conditions": [ALL, SUBTREE],
    },
    {
        "resource": "customers",
        "action": "update",
        "name": "Редактирование заказчиков",
        "conditions": [ALL, SUBTREE],
    },
    # SUPPLIERS
    {
        "resource": "suppliers",
        "action": "create",
        "name": "Создание поставщиков",
        "conditions": [ALL],
    },
    {
        "resource": "suppliers",
        "action": "read",
        "name": "Просмотр поставщиков",
        "conditions": [ALL],
    },
    {
        "resource": "suppliers",
        "action": "update",
        "name": "Редактирование поставщиков",
        "conditions": [ALL],
    },
    {
        "resource": "suppliers",
        "action": "delete",
        "name": "Удаление поставщиков",
        "conditions": [ALL],
    },
    # MEDIA
    {"resource": "media", "action": "create", "name": "Загрузка медиа", "conditions": [ALL]},
    {"resource": "media", "action": "read", "name": "Просмотр медиа", "conditions": [ALL]},
    {
        "resource": "media",
        "action": "delete",
        "name": "Удаление медиа",
        "conditions": [ALL, CREATOR],
    },
    # SETTINGS
    {"resource": "settings", "action": "read", "name": "Просмотр настроек", "conditions": [ALL]},
    {
        "resource": "settings",
        "action": "update",
        "name": "Редактирование настроек",
        "conditions": [ALL],
    },
    # AUDIT LOG
    {"resource": "audit_log", "action": "read", "name": "Просмотр логов", "conditions": [ALL]},
]
