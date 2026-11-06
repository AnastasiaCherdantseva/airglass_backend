"""
Seed-данные для значений атрибутов.
"""

ATTRIBUTE_OPTIONS = {
    "effort": [
        {"value": "25-40кг", "code": "effort_25_40_kg", "sort_order": 1},
        {"value": "40-65 кг", "code": "effort_40_65_kg", "sort_order": 2},
        {"value": "65-85", "code": "effort_65_85", "sort_order": 3},
    ],
    "glass_hole_diameter": [
        {"value": "не требуется", "code": "glass_hole_not_required", "sort_order": 1},
        {"value": "6-8 мм", "code": "glass_hole_6_8_mm", "sort_order": 2},
        {"value": "8-10 мм", "code": "glass_hole_8_10_mm", "sort_order": 3},
        {"value": "10-12 мм", "code": "glass_hole_10_12_mm", "sort_order": 4},
    ],
    "glass_thickness": [
        {"value": "2", "code": "glass_thickness_2", "sort_order": 1},
        {"value": "4", "code": "glass_thickness_4", "sort_order": 2},
        {"value": "5", "code": "glass_thickness_5", "sort_order": 3},
        {"value": "6", "code": "glass_thickness_6", "sort_order": 4},
        {"value": "8", "code": "glass_thickness_8", "sort_order": 5},
        {"value": "10", "code": "glass_thickness_10", "sort_order": 6},
        {"value": "12", "code": "glass_thickness_12", "sort_order": 7},
    ],
    "type": [
        {"value": "Шайба разрыва", "code": "type_washer_break", "sort_order": 1},
        {"value": "Втулка разрыва", "code": "type_bushing_break", "sort_order": 2},
        {"value": "Пятак", "code": "type_pyatak", "sort_order": 3},
        {"value": "Крепление", "code": "type_mount", "sort_order": 4},
        {"value": "Штанга", "code": "type_rod", "sort_order": 5},
        {"value": "Стойка", "code": "type_post", "sort_order": 6},
    ],
    "wall_mount": [
        {"value": "Одно отверстие", "code": "wall_mount_one_hole", "sort_order": 1},
        {"value": "Два отверстия", "code": "wall_mount_two_holes", "sort_order": 2},
        {"value": "Одностороннее", "code": "wall_mount_one_sided", "sort_order": 3},
        {"value": "Двусторонее", "code": "wall_mount_two_sided", "sort_order": 4},
    ],
    "connection": [
        {"value": "Стекло-стекло", "code": "connection_glass_glass", "sort_order": 1},
        {"value": "Стена-стекло", "code": "connection_wall_glass", "sort_order": 2},
        {
            "value": "Потолок-стекло и пол-стекло",
            "code": "connection_ceiling_floor_glass",
            "sort_order": 3,
        },
        {"value": "К фрамуге", "code": "connection_to_transom", "sort_order": 4},
        {"value": "Труба-стекло", "code": "connection_pipe_glass", "sort_order": 5},
        {"value": "Держатель штанги", "code": "connection_rod_holder", "sort_order": 6},
    ],
    "mounting_angle": [
        {"value": "90", "code": "mounting_angle_90", "sort_order": 1},
        {"value": "135", "code": "mounting_angle_135", "sort_order": 2},
        {"value": "180", "code": "mounting_angle_180", "sort_order": 3},
    ],
    "opening": [
        {"value": "Маятниковые(в обе стороны)", "code": "opening_pendulum_both", "sort_order": 1},
        {"value": "Распашные (в одну сторону)", "code": "opening_swing_one", "sort_order": 2},
    ],
    "soft_close": [
        {"value": "Пружинный довод", "code": "self_closing_spring", "sort_order": 1},
        {"value": "Лифтовый механизм", "code": "self_closing_lift", "sort_order": 2},
        {"value": "Без довода", "code": "self_closing_none", "sort_order": 3},
        {"value": "Гидравлический довод", "code": "self_closing_hydraulic", "sort_order": 4},
    ],
    "side": [
        {"value": "Правая", "code": "side_right", "sort_order": 1},
        {"value": "Левая", "code": "side_left", "sort_order": 2},
    ],
    "rotation_angle": [
        {"value": "90", "code": "rotation_angle_90", "sort_order": 1},
        {"value": "93", "code": "rotation_angle_93", "sort_order": 2},
        {"value": "105", "code": "rotation_angle_105", "sort_order": 3},
        {"value": "114", "code": "rotation_angle_114", "sort_order": 4},
        {"value": "135", "code": "rotation_angle_135", "sort_order": 5},
        {"value": "140", "code": "rotation_angle_140", "sort_order": 6},
        {"value": "155", "code": "rotation_angle_155", "sort_order": 7},
        {"value": "180", "code": "rotation_angle_180", "sort_order": 8},
        {"value": "188", "code": "rotation_angle_188", "sort_order": 9},
        {"value": "360", "code": "rotation_angle_360", "sort_order": 10},
    ],
    "pendulum_system": [
        {"value": "Классика", "code": "pendulum_system_classic", "sort_order": 1},
        {"value": "Вектор", "code": "pendulum_system_vector", "sort_order": 2},
    ],
    "floor_door_closer_type": [
        {"value": "Открытый монтаж", "code": "floor_door_closer_open_mount", "sort_order": 1},
        {"value": "Скрытый монтаж", "code": "floor_door_closer_hidden_mount", "sort_order": 2},
    ],
    "cylinder_mechanism": [
        {"value": "ключ-ключ", "code": "cylinder_mechanism_key_key", "sort_order": 1},
        {"value": "Ключ-вертушка", "code": "cylinder_mechanism_key_turn", "sort_order": 2},
        {"value": "сантехнический", "code": "cylinder_mechanism_sanitary", "sort_order": 3},
        {"value": "Без цилиндра", "code": "cylinder_mechanism_none", "sort_order": 4},
    ],
    "fixer_type": [
        {"value": "Металл", "code": "fixer_type_metal", "sort_order": 1},
        {"value": "Магнитный", "code": "fixer_type_magnetic", "sort_order": 2},
    ],
    "cylinder_size": [
        {"value": "20/35", "code": "cylinder_size_20_35", "sort_order": 1},
        {"value": "30/30", "code": "cylinder_size_30_30", "sort_order": 2},
        {"value": "22/27", "code": "cylinder_size_22_27", "sort_order": 3},
    ],
    "groove_size": [
        {"value": "24х24", "code": "groove_size_24_24_cyr", "sort_order": 1},
        {"value": "14*14", "code": "groove_size_14_14", "sort_order": 2},
        {"value": "24x24", "code": "groove_size_24_24_lat", "sort_order": 3},
        {"value": "27x30", "code": "groove_size_27_30_lat", "sort_order": 4},
        {"value": "27x27", "code": "groove_size_27_27_lat", "sort_order": 5},
        {"value": "27х30", "code": "groove_size_27_30_cyr", "sort_order": 6},
    ],
    "handle_variant": [
        {"value": "шарнирный", "code": "handle_variant_hinged", "sort_order": 1},
        {"value": "бесшарнирный", "code": "handle_variant_non_hinged", "sort_order": 2},
    ],
    "adjustment": [
        {"value": "отклонение", "code": "adjustment_deviation", "sort_order": 1},
        {"value": "Регулируемое 14.5-16 мм", "code": "adjustment_14_5_16_mm", "sort_order": 2},
        {"value": "Регулируемое 18-22 мм", "code": "adjustment_18_22_mm", "sort_order": 3},
        {"value": "Нерегулируемое 6 мм", "code": "adjustment_fixed_6_mm", "sort_order": 4},
        {"value": "Регулируемое 8,5-11 мм", "code": "adjustment_8_5_11_mm", "sort_order": 5},
        {"value": "Регулируемое 10,5-12,5", "code": "adjustment_10_5_12_5", "sort_order": 6},
        {"value": "Регулируемое 10,5-12,5 мм", "code": "adjustment_10_5_12_5_mm", "sort_order": 7},
    ],
    "manufacturing_method": [
        {"value": "Штампованный", "code": "manufacturing_method_stamped", "sort_order": 1},
        {"value": "Литой", "code": "manufacturing_method_cast", "sort_order": 2},
    ],
}
