"""
Seed-данные для глобальных правил галереи.

Правило = набор условий по категориям каталога.
`category_code` в условиях — это `code` из app/db/seed/categories.py.
"""

GALLERY_RULES = [
    {
        "code": "glass_8mm_only",
        "name": "Только стекло",
        "description": "Фотографии меняются в зависимости от стекла",
        "sort_order": 1,
        "is_active": True,
        "conditions": [
            {"category_code": "glass_8mm"},
        ],
    },
    {
        "code": "glass_8mm_sliding_shower_systems",
        "name": "Стекло + Раздвижка",
        "description": "Фотографии меняются в зависимости от стекла и раздвижной системы",
        "sort_order": 2,
        "is_active": True,
        "conditions": [
            {"category_code": "glass_8mm"},
            {"category_code": "sliding_shower_systems"},
        ],
    },
]