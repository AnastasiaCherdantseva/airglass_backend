"""
Seed-данные для ролей.
"""

ROLES = [
    {
        "code": "SYSTEM_ADMIN",
        "name": "Системный администратор",
        "description": "Полный доступ ко всем функциям системы",
        "is_system": True,
        "is_active": True,
    },
    {
        "code": "MANAGER",
        "name": "Менеджер",
        "description": "Работа с клиентами, создание КП",
        "is_system": True,
        "is_active": True,
    },
    {
        "code": "ENGINEER",
        "name": "Инженер",
        "description": "Расчёты, создание шаблонов, работа с каталогом",
        "is_system": True,
        "is_active": True,
    },
    {
        "code": "VIEWER",
        "name": "Наблюдатель",
        "description": "Только просмотр данных",
        "is_system": True,
        "is_active": True,
    },
]