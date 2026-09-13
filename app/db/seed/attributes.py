"""
Seed-данные для атрибутов.

"""

ATTRIBUTES = [
    # ==========================================
    # OPTION
    # ==========================================
    {
        "code": "furniture_class",
        "name": "Класс фурнитуры",
        "data_type": "OPTION",
        "is_filterable": True,
        "is_required": False,
    },
    {
        "code": "opening_type",
        "name": "Тип открывания",
        "data_type": "OPTION",
        "is_filterable": True,
        "is_required": False,
    },
    {
        "code": "opening_direction",
        "name": "Открывание",
        "data_type": "OPTION",
        "is_filterable": True,
        "is_required": False,
    },
    {
        "code": "features",
        "name": "Особенности",
        "data_type": "OPTION",
        "is_filterable": True,
        "is_required": False,
    },

    # ==========================================
    # DECIMAL
    # ==========================================
    {
        "code": "glass_thickness",
        "name": "Толщина стекла",
        "data_type": "DECIMAL",
        "is_filterable": True,
        "is_required": False,
        "unit_code": "mm",
    },
    {
        "code": "length",
        "name": "Длина",
        "data_type": "DECIMAL",
        "is_filterable": True,
        "is_required": False,
        "unit_code": "meter",
    },
    {
        "code": "metal_thickness",
        "name": "Толщина металла",
        "data_type": "DECIMAL",
        "is_filterable": True,
        "is_required": False,
        "unit_code": "mm",
    },
]