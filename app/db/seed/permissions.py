"""
Seed-данные для прав и их вариантов (PermissionCondition).

Права: resource.action (7 действий).
Варианты: type (all | category | role | creator | subtree) + effect (allow | deny).
is_system: системное право (нельзя удалить).
"""

from typing import TypedDict


class PermissionConditionSeed(TypedDict, total=False):
    type: str
    effect: str
    category_id: str
    role_id: str


class PermissionSeed(TypedDict):
    code: str
    name: str
    resource: str
    action: str
    is_system: bool
    conditions: list[PermissionConditionSeed]


PERMISSIONS: list[PermissionSeed] = [
    # ============================================
    # CALCULATOR
    # ============================================
    {
        "code": "calculator.read",
        "name": "Доступ к калькулятору",
        "resource": "calculator",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # USERS
    # ============================================
    {
        "code": "users.create",
        "name": "Создание пользователей",
        "resource": "users",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "users.read",
        "name": "Просмотр пользователей",
        "resource": "users",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "users.update",
        "name": "Редактирование пользователей",
        "resource": "users",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "users.delete",
        "name": "Удаление пользователей",
        "resource": "users",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    # ============================================
    # ROLES
    # ============================================
    {
        "code": "roles.create",
        "name": "Создание ролей",
        "resource": "roles",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "roles.read",
        "name": "Просмотр ролей",
        "resource": "roles",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "roles.update",
        "name": "Редактирование ролей",
        "resource": "roles",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "roles.delete",
        "name": "Удаление ролей",
        "resource": "roles",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    # ============================================
    # PRODUCTS
    # ============================================
    {
        "code": "products.create",
        "name": "Создание товаров",
        "resource": "products",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.read",
        "name": "Просмотр товаров",
        "resource": "products",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.update",
        "name": "Редактирование товаров",
        "resource": "products",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.delete",
        "name": "Удаление товаров",
        "resource": "products",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.archive",
        "name": "Архивация товаров",
        "resource": "products",
        "action": "archive",
        "is_system": False,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.export",
        "name": "Экспорт товаров",
        "resource": "products",
        "action": "export",
        "is_system": False,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "products.import",
        "name": "Импорт товаров",
        "resource": "products",
        "action": "import",
        "is_system": False,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # CATEGORIES
    # ============================================
    {
        "code": "categories.create",
        "name": "Создание категорий",
        "resource": "categories",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "categories.read",
        "name": "Просмотр категорий",
        "resource": "categories",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "categories.update",
        "name": "Редактирование категорий",
        "resource": "categories",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "categories.delete",
        "name": "Удаление категорий",
        "resource": "categories",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # TEMPLATES
    # ============================================
    {
        "code": "templates.create",
        "name": "Создание шаблонов",
        "resource": "templates",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "templates.read",
        "name": "Просмотр шаблонов",
        "resource": "templates",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "templates.update",
        "name": "Редактирование шаблонов",
        "resource": "templates",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "templates.delete",
        "name": "Удаление шаблонов",
        "resource": "templates",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    # ============================================
    # QUOTES
    # ============================================
    {
        "code": "quotes.create",
        "name": "Создание КП",
        "resource": "quotes",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "quotes.read",
        "name": "Просмотр КП",
        "resource": "quotes",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "quotes.update",
        "name": "Редактирование КП",
        "resource": "quotes",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "quotes.delete",
        "name": "Удаление КП",
        "resource": "quotes",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "quotes.export",
        "name": "Экспорт КП",
        "resource": "quotes",
        "action": "export",
        "is_system": False,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # PROJECTS
    # ============================================
    {
        "code": "projects.create",
        "name": "Создание проектов",
        "resource": "projects",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "projects.read",
        "name": "Просмотр проектов",
        "resource": "projects",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "projects.update",
        "name": "Редактирование проектов",
        "resource": "projects",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    {
        "code": "projects.archive",
        "name": "Архивация проектов",
        "resource": "projects",
        "action": "archive",
        "is_system": False,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # CUSTOMERS
    # ============================================
    {
        "code": "customers.create",
        "name": "Создание заказчиков",
        "resource": "customers",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "customers.read",
        "name": "Просмотр заказчиков",
        "resource": "customers",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    {
        "code": "customers.update",
        "name": "Редактирование заказчиков",
        "resource": "customers",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "subtree", "effect": "allow"},
        ],
    },
    # ============================================
    # SUPPLIERS
    # ============================================
    {
        "code": "suppliers.create",
        "name": "Создание поставщиков",
        "resource": "suppliers",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "suppliers.read",
        "name": "Просмотр поставщиков",
        "resource": "suppliers",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "suppliers.update",
        "name": "Редактирование поставщиков",
        "resource": "suppliers",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "suppliers.delete",
        "name": "Удаление поставщиков",
        "resource": "suppliers",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # ============================================
    # MEDIA
    # ============================================
    {
        "code": "media.create",
        "name": "Загрузка медиа",
        "resource": "media",
        "action": "create",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "media.read",
        "name": "Просмотр медиа",
        "resource": "media",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "media.delete",
        "name": "Удаление медиа",
        "resource": "media",
        "action": "delete",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
            {"type": "creator", "effect": "allow"},
        ],
    },
    # ============================================
    # SETTINGS
    # ============================================
    # {
    #     "code": "settings.create",
    #     "name": "Создание настроек",
    #     "resource": "settings",
    #     "action": "create",
    #     "is_system": True,
    #     "conditions": [
    #         {"type": "all", "effect": "allow"},
    #     ],
    # },
    {
        "code": "settings.read",
        "name": "Просмотр настроек",
        "resource": "settings",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    {
        "code": "settings.update",
        "name": "Редактирование настроек",
        "resource": "settings",
        "action": "update",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
    # {
    #     "code": "settings.delete",
    #     "name": "Удаление настроек",
    #     "resource": "settings",
    #     "action": "delete",
    #     "is_system": True,
    #     "conditions": [
    #         {"type": "all", "effect": "allow"},
    #     ],
    # },
    # ============================================
    # AUDIT LOG
    # ============================================
    {
        "code": "audit_log.read",
        "name": "Просмотр логов",
        "resource": "audit_log",
        "action": "read",
        "is_system": True,
        "conditions": [
            {"type": "all", "effect": "allow"},
        ],
    },
]
