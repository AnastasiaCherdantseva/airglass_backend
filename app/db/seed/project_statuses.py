"""
Seed-данные для статусов проектов.
"""

PROJECT_STATUSES = [
    {
        "code": "DRAFT",
        "name": "Черновик",
        "sort_order": 1,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "CALCULATION",
        "name": "Расчёт",
        "sort_order": 2,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "QUOTE_SENT",
        "name": "КП отправлено",
        "sort_order": 3,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "NEGOTIATION",
        "name": "Переговоры",
        "sort_order": 4,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "APPROVED",
        "name": "Согласовано",
        "sort_order": 5,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "IN_PRODUCTION",
        "name": "В производстве",
        "sort_order": 6,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "INSTALLATION",
        "name": "Монтаж",
        "sort_order": 7,
        "is_final": False,
        "is_active": True,
    },
    {
        "code": "COMPLETED",
        "name": "Завершено",
        "sort_order": 8,
        "is_final": True,
        "is_active": True,
    },
    {
        "code": "CANCELLED",
        "name": "Отменено",
        "sort_order": 9,
        "is_final": True,
        "is_active": True,
    },
    {
        "code": "ARCHIVE",
        "name": "В архиве",
        "sort_order": 10,
        "is_final": True,
        "is_active": True,
    },
]