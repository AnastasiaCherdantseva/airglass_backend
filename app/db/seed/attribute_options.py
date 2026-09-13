"""
Seed-данные для значений атрибутов.
"""

ATTRIBUTE_OPTIONS = {
    # ==========================================
    # КЛАСС ФУРНИТУРЫ
    # ==========================================
    "furniture_class": [
        {"value": "премиум", "code": "premium", "sort_order": 1},
        {"value": "стандарт", "code": "standard", "sort_order": 2},
        {"value": "эконом", "code": "econom", "sort_order": 3},
    ],

    # ==========================================
    # ТИП ОТКРЫВАНИЯ
    # ==========================================
    "opening_type": [
        {"value": "раздвижная дверь", "code": "sliding_door", "sort_order": 1},
        {"value": "распашная дверь", "code": "swing_door", "sort_order": 2},
        {"value": "гармошка", "code": "accordion", "sort_order": 3},
        {"value": "по 90° в каждую сторону", "code": "90_both", "sort_order": 4},
    ],

    # ==========================================
    # ОТКРЫВАНИЕ
    # ==========================================
    "opening_direction": [
        {"value": "90° внутрь", "code": "90_in", "sort_order": 1},
        {"value": "90° наружу", "code": "90_out", "sort_order": 2},
        {"value": "180° в одну сторону", "code": "180_one", "sort_order": 3},
        {"value": "стекло-стекло 180°", "code": "glass_glass_180", "sort_order": 4},
        {"value": "стекло-стекло 135°", "code": "glass_glass_135", "sort_order": 5},
        {"value": "стекло-стекло 90°", "code": "glass_glass_90", "sort_order": 6},
        {"value": "стекло-стекло 0°-180°", "code": "glass_glass_0_180", "sort_order": 7},
        {"value": "стена-стекло 180°", "code": "wall_glass_180", "sort_order": 8},
        {"value": "стена-стекло 135°", "code": "wall_glass_135", "sort_order": 9},
        {"value": "стена-стекло 90°", "code": "wall_glass_90", "sort_order": 10},
        {"value": "стена-стекло 0°-180°", "code": "wall_glass_0_180", "sort_order": 11},
        {"value": "стекло-пол", "code": "glass_floor", "sort_order": 12},
        {"value": "труба-стена", "code": "pipe_wall", "sort_order": 13},
        {"value": "труба-труба", "code": "pipe_pipe", "sort_order": 14},
        {"value": "труба-стекло", "code": "pipe_glass", "sort_order": 15},
    ],

    # ==========================================
    # ОСОБЕННОСТИ
    # ==========================================
    "features": [
        {"value": "магнитный", "code": "magnetic", "sort_order": 1},
        {"value": "самоклеющийся", "code": "self_adhesive", "sort_order": 2},
        {"value": "А-образный", "code": "a_shaped", "sort_order": 3},
        {"value": "С-образный", "code": "c_shaped", "sort_order": 4},
        {"value": "F-образный", "code": "f_shaped", "sort_order": 5},
        {"value": "Y-образный", "code": "y_shaped", "sort_order": 6},
        {"value": "Ш-образный", "code": "sh_shaped", "sort_order": 7},
        {"value": "Ч-образный", "code": "ch_shaped", "sort_order": 8},
        {"value": "нижний", "code": "bottom", "sort_order": 9},
        {"value": "гармошка", "code": "accordion", "sort_order": 10},
        {"value": "угловой", "code": "corner", "sort_order": 11},
        {"value": "микролифт", "code": "microlift", "sort_order": 12},
        {"value": "декоративные накладки", "code": "decorative_covers", "sort_order": 13},
        {"value": "декоративные крышки", "code": "decorative_caps", "sort_order": 14},
        {"value": "пружинный доводчик", "code": "spring_closer", "sort_order": 15},
        {"value": "регулировка 0 положения", "code": "zero_position_adjustment", "sort_order": 16},
        {"value": "гидравлический доводчик", "code": "hydraulic_closer", "sort_order": 17},
        {"value": "регулировка скорости доводчика", "code": "closer_speed_adjustment", "sort_order": 18},
        {"value": "фиксация на 90°", "code": "fix_90", "sort_order": 19},
        {"value": "без реза уплотнителя", "code": "without_seal_cut", "sort_order": 20},
        {"value": "другое", "code": "other", "sort_order": 99},
    ],
}