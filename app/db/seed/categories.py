"""
Seed-данные для категорий (дерево).

Структура: (id, parent_code, name, code, sort_order)

⚠️ Подкатегории-материалы/серии/типы схлопнуты в родительские категории.
"""

CATEGORIES = [
    # ============================================
    # 1. ДВЕРНЫЕ ДОВОДЧИКИ
    # ============================================
    {
        "code": "door_closers",
        "parent_code": None,
        "name": "Дверные доводчики",
        "sort_order": 1,
    },

    # ============================================
    # 2. ДИСТАНЦИОННЫЕ ДЕРЖАТЕЛИ
    # ============================================
    {
        "code": "remote_holders",
        "parent_code": None,
        "name": "Дистанционные держатели",
        "sort_order": 2,
    },
    {
        "code": "aluminum_holders",
        "parent_code": "remote_holders",
        "name": "Алюминиевые держатели",
        "sort_order": 1,
    },
    {
        "code": "holders_without_drilling",
        "parent_code": "remote_holders",
        "name": "Держатели без сверления",
        "sort_order": 2,
    },
    {
        "code": "desktop_sign_holders",
        "parent_code": "remote_holders",
        "name": "Держатели настольных табличек",
        "sort_order": 3,
    },
    {
        "code": "cone_holders",
        "parent_code": "remote_holders",
        "name": "Конусные держатели",
        "sort_order": 4,
    },
    {
        "code": "metal_holders",
        "parent_code": "remote_holders",
        "name": "Металлические держатели",
        "sort_order": 5,
    },

    # ============================================
    # 3. ДЛЯ ВИТРИН И МЕБЕЛИ ИЗ СТЕКЛА
    # ============================================
    {
        "code": "glass_showcases_furniture",
        "parent_code": None,
        "name": "Для витрин и мебели из стекла",
        "sort_order": 3,
    },
    {
        "code": "facade_dampers",
        "parent_code": "glass_showcases_furniture",
        "name": "Амортизаторы для фасадов",
        "sort_order": 1,
    },
    {
        "code": "bushings_plugs_washers_connectors",
        "parent_code": "glass_showcases_furniture",
        "name": "Втулки, фишки, шайбы, соединители",
        "sort_order": 2,
    },
    {
        "code": "glass_tables",
        "parent_code": "glass_showcases_furniture",
        "name": "Для стеклянных столов",
        "sort_order": 3,
    },
    {
        "code": "glass_showcase_locks",
        "parent_code": "glass_showcases_furniture",
        "name": "Замки для стеклянных витрин",
        "sort_order": 4,
    },
    {
        "code": "glass_furniture_hinges",
        "parent_code": "glass_showcases_furniture",
        "name": "Петли для мебели из стекла",
        "sort_order": 5,
    },
    {
        "code": "glass_shelf_holders",
        "parent_code": "glass_showcases_furniture",
        "name": "Полкодержатели для стекла",
        "sort_order": 6,
    },
    {
        "code": "glass_showcase_handles",
        "parent_code": "glass_showcases_furniture",
        "name": "Ручки для стеклянных витрин",
        "sort_order": 7,
    },
    {
        "code": "stoppers_fixers_rollers",
        "parent_code": "glass_showcases_furniture",
        "name": "Стопора, фиксаторы, ролики",
        "sort_order": 8,
    },
    {
        "code": "cable_system",
        "parent_code": "glass_showcases_furniture",
        "name": "Тросовая система",
        "sort_order": 9,
    },

    # ============================================
    # 4. ДЛЯ ДУШЕВЫХ ИЗ СТЕКЛА
    # ============================================
    {
        "code": "glass_showers",
        "parent_code": None,
        "name": "Для душевых из стекла",
        "sort_order": 4,
    },
    {
        "code": "glass_8mm",
        "parent_code": "glass_showers",
        "name": "Стекло 8мм",
        "sort_order": 1,
    },
    {
        "code": "bathroom_accessories",
        "parent_code": "glass_showers",
        "name": "Аксессуары для ванной",
        "sort_order": 2,
    },
    {
        "code": "shower_cabin_locks",
        "parent_code": "glass_showers",
        "name": "Замки для душевых кабин",
        "sort_order": 3,
    },
    {
        "code": "hendlex_protective_coatings",
        "parent_code": "glass_showers",
        "name": "Защитные покрытия HENDLEX",
        "sort_order": 4,
    },
    {
        "code": "rod_hinge_kit",
        "parent_code": "glass_showers",
        "name": "Комплект штанга-петля",
        "sort_order": 5,
    },
    {
        "code": "shower_cabin_connectors",
        "parent_code": "glass_showers",
        "name": "Коннекторы для душевых кабин",
        "sort_order": 6,
    },
    {
        "code": "top_frame_rod_connectors",
        "parent_code": "glass_showers",
        "name": "Коннекторы для штанг верхней обвязки",
        "sort_order": 7,
    },
    {
        "code": "shower_cabin_hinges",
        "parent_code": "glass_showers",
        "name": "Петли для душевых кабин",
        "sort_order": 8,
    },
    {
        "code": "aluminum_profiles",
        "parent_code": "glass_showers",
        "name": "Профили из алюминия",
        "sort_order": 9,
    },
    {
        "code": "u_shaped_profile_aisi304",
        "parent_code": "glass_showers",
        "name": "Профиль п-образный AISI304",
        "sort_order": 10,
    },
    {
        "code": "sliding_shower_systems",
        "parent_code": "glass_showers",
        "name": "Раздвижные душевые системы",
        "sort_order": 11,
    },
    {
        "code": "consumables",
        "parent_code": "glass_showers",
        "name": "Расходные материалы",
        "sort_order": 12,
    },
    {
        "code": "adjustable_stabilization_rods",
        "parent_code": "glass_showers",
        "name": "Регулируемые стабилизационные штанги",
        "sort_order": 13,
    },
    {
        "code": "shower_handles",
        "parent_code": "glass_showers",
        "name": "Ручки для душевых",
        "sort_order": 14,
    },
    {
        "code": "silicones_sealants",
        "parent_code": "glass_showers",
        "name": "Силиконы и герметики",
        "sort_order": 15,
    },
    {
        "code": "shower_stoppers",
        "parent_code": "glass_showers",
        "name": "Стопоры",
        "sort_order": 16,
    },
    {
        "code": "shower_rods_tracks",
        "parent_code": "glass_showers",
        "name": "Трубы (штанги верхней обвязки/треки) для душевых кабин",
        "sort_order": 17,
    },
    {
        "code": "shower_seals",
        "parent_code": "glass_showers",
        "name": "Уплотнители для душевых",
        "sort_order": 18,
    },

    # ============================================
    # 5. ДЛЯ МАЯТНИКОВЫХ ДВЕРЕЙ
    # ============================================
    {
        "code": "pendulum_doors",
        "parent_code": None,
        "name": "Для маятниковых дверей",
        "sort_order": 5,
    },
    {
        "code": "classic_holders",
        "parent_code": "pendulum_doors",
        "name": "Держатели «Классика»",
        "sort_order": 1,
    },
    {
        "code": "floor_door_closer",
        "parent_code": "pendulum_doors",
        "name": "Доводчик напольный",
        "sort_order": 2,
    },
    {
        "code": "pendulum_locks",
        "parent_code": "pendulum_doors",
        "name": "Замки",
        "sort_order": 3,
    },
    {
        "code": "entrance_door_handles",
        "parent_code": "pendulum_doors",
        "name": "Ручки для входных дверей",
        "sort_order": 4,
    },
    {
        "code": "handles_with_lock",
        "parent_code": "pendulum_doors",
        "name": "Ручки с замком",
        "sort_order": 5,
    },
    {
        "code": "vector_system",
        "parent_code": "pendulum_doors",
        "name": "Система Вектор",
        "sort_order": 6,
    },
    {
        "code": "classic_system",
        "parent_code": "pendulum_doors",
        "name": "Система Классика",
        "sort_order": 7,
    },
    {
        "code": "pendulum_system_8300",
        "parent_code": "pendulum_doors",
        "name": "Система маятниковых дверей 8300",
        "sort_order": 8,
    },
    {
        "code": "door_stop",
        "parent_code": "pendulum_doors",
        "name": "Упор дверной",
        "sort_order": 9,
    },
    {
        "code": "snd_ea",
        "parent_code": "pendulum_doors",
        "name": "SND EA",
        "sort_order": 10,
    },

    # ============================================
    # 6. ДЛЯ МЕЖКОМНАТНЫХ ДВЕРЕЙ
    # ============================================
    {
        "code": "interior_doors",
        "parent_code": None,
        "name": "Для межкомнатных дверей",
        "sort_order": 6,
    },
    {
        "code": "interior_locks",
        "parent_code": "interior_doors",
        "name": "Замки межкомнатные",
        "sort_order": 1,
    },
    {
        "code": "glass_door_frames",
        "parent_code": "interior_doors",
        "name": "Коробки для стеклянных дверей",
        "sort_order": 2,
    },
    {
        "code": "lock_cylinders",
        "parent_code": "interior_doors",
        "name": "Личинки (личины) замка",
        "sort_order": 3,
    },
    {
        "code": "glass_interior_door_hinges",
        "parent_code": "interior_doors",
        "name": "Петли для стеклянных межкомнатных дверей",
        "sort_order": 4,
    },

    # ============================================
    # 7. ЗАЖИМНЫЕ ПРОФИЛИ
    # ============================================
    {
        "code": "clamping_profiles",
        "parent_code": None,
        "name": "Зажимные профили",
        "sort_order": 7,
    },
    {
        "code": "clamping_profile_100mm",
        "parent_code": "clamping_profiles",
        "name": "Зажимной профиль 100мм для стеклянных ограждений",
        "sort_order": 1,
    },
    {
        "code": "clamping_profile_l",
        "parent_code": "clamping_profiles",
        "name": "Зажимной профиль серии L",
        "sort_order": 2,
    },
    {
        "code": "clamping_profile_sindikat",
        "parent_code": "clamping_profiles",
        "name": "Зажимной профиль Синдикат",
        "sort_order": 3,
    },
    {
        "code": "support_profile",
        "parent_code": "clamping_profiles",
        "name": "Опорный профиль",
        "sort_order": 4,
    },

    # ============================================
    # 8. ЗАМКИ ДЛЯ СТЕКЛЯННЫХ ДВЕРЕЙ
    # ============================================
    {
        "code": "glass_door_locks",
        "parent_code": None,
        "name": "Замки для стеклянных дверей",
        "sort_order": 8,
    },
    {
        "code": "mechanical_glass_locks",
        "parent_code": "glass_door_locks",
        "name": "Замки механические для стекла",
        "sort_order": 1,
    },
    {
        "code": "push_handle_glass_locks",
        "parent_code": "glass_door_locks",
        "name": "Замки c нажимной ручкой для стеклянных дверей",
        "sort_order": 2,
    },

    # ============================================
    # 9. ИЗДЕЛИЯ ИЗ НЕРЖАВЕЮЩЕЙ СТАЛИ
    # ============================================
    {
        "code": "stainless_steel_products",
        "parent_code": None,
        "name": "Изделия из нержавеющей стали",
        "sort_order": 9,
    },

    # ============================================
    # 10. ИНСТРУМЕНТ И МАТЕРИАЛЫ ДЛЯ ОБРАБОТКИ СТЕКЛА
    # ============================================
    {
        "code": "glass_processing_tools_materials",
        "parent_code": None,
        "name": "Инструмент и материалы для обработки стекла",
        "sort_order": 10,
    },
    {
        "code": "manual_glass_cutting_tools",
        "parent_code": "glass_processing_tools_materials",
        "name": "Инструмент для ручной резки стекла",
        "sort_order": 1,
    },
    {
        "code": "matting_liquid_paste",
        "parent_code": "glass_processing_tools_materials",
        "name": "Матирующая жидкость и паста",
        "sort_order": 2,
    },
    {
        "code": "cerium_oxide",
        "parent_code": "glass_processing_tools_materials",
        "name": "Оксид церия",
        "sort_order": 3,
    },
    {
        "code": "foam_sealant_gun",
        "parent_code": "glass_processing_tools_materials",
        "name": "Пистолет для пены и герметика",
        "sort_order": 4,
    },
    {
        "code": "glass_carrying_suction_cups",
        "parent_code": "glass_processing_tools_materials",
        "name": "Присоски для переноски стекла",
        "sort_order": 5,
    },
    {
        "code": "tension_belts",
        "parent_code": "glass_processing_tools_materials",
        "name": "Ремни стяжные",
        "sort_order": 6,
    },
    {
        "code": "satinator",
        "parent_code": "glass_processing_tools_materials",
        "name": "Сатинатор",
        "sort_order": 7,
    },
    {
        "code": "glass_drills",
        "parent_code": "glass_processing_tools_materials",
        "name": "Сверла по стеклу",
        "sort_order": 8,
    },
    {
        "code": "glass_transport_corner",
        "parent_code": "glass_processing_tools_materials",
        "name": "Уголок транспортировочный для стекла",
        "sort_order": 9,
    },
    {
        "code": "uv_bonding",
        "parent_code": "glass_processing_tools_materials",
        "name": "УФ-склейка",
        "sort_order": 10,
    },
    {
        "code": "electrocorundum",
        "parent_code": "glass_processing_tools_materials",
        "name": "Электрокорунд",
        "sort_order": 11,
    },

    # ============================================
    # 11. КРЕПЕЖНЫЕ ИЗДЕЛИЯ
    # ============================================
    {
        "code": "fasteners",
        "parent_code": None,
        "name": "Крепежные изделия",
        "sort_order": 11,
    },
    {
        "code": "anchors",
        "parent_code": "fasteners",
        "name": "Анкера",
        "sort_order": 1,
    },
    {
        "code": "stainless_fasteners",
        "parent_code": "fasteners",
        "name": "Метизы из нержавеющей стали",
        "sort_order": 2,
    },
    {
        "code": "studs",
        "parent_code": "fasteners",
        "name": "Шпильки",
        "sort_order": 3,
    },

    # ============================================
    # 12. МЕБЕЛЬНАЯ ФУРНИТУРА
    # ============================================
    {
        "code": "furniture_hardware",
        "parent_code": None,
        "name": "Мебельная фурнитура",
        "sort_order": 12,
    },
    {
        "code": "mail_locks",
        "parent_code": "furniture_hardware",
        "name": "Замки почтовые",
        "sort_order": 1,
    },
    {
        "code": "panel_locks",
        "parent_code": "furniture_hardware",
        "name": "Замки щитовые",
        "sort_order": 2,
    },
    {
        "code": "wardrobe_sliding_rollers",
        "parent_code": "furniture_hardware",
        "name": "Ролики для шкафа купе",
        "sort_order": 3,
    },
    {
        "code": "door_stops",
        "parent_code": "furniture_hardware",
        "name": "Упоры дверные",
        "sort_order": 4,
    },

    # ============================================
    # 13. МЕБЕЛЬНЫЕ КОЛЕСА И КОЛЕСНЫЕ РОЛИКИ ДЛЯ МЕБЕЛИ
    # ============================================
    {
        "code": "furniture_wheels_rollers",
        "parent_code": None,
        "name": "Мебельные колеса и колесные ролики для мебели",
        "sort_order": 13,
    },
    {
        "code": "hardware_wheels",
        "parent_code": "furniture_wheels_rollers",
        "name": "Аппаратные колеса",
        "sort_order": 1,
    },
    {
        "code": "waste_container_wheels",
        "parent_code": "furniture_wheels_rollers",
        "name": "Колеса для мусорных контейнеров",
        "sort_order": 2,
    },
    {
        "code": "furniture_wheel",
        "parent_code": "furniture_wheels_rollers",
        "name": "Колесо мебельное",
        "sort_order": 3,
    },
    {
        "code": "industrial_rubber_wheels",
        "parent_code": "furniture_wheels_rollers",
        "name": "Промышленные колеса серия резина",
        "sort_order": 4,
    },

    # ============================================
    # 14. НЕРЖАВЕЮЩИЕ ПОРУЧНИ С ПАЗОМ
    # ============================================
    {
        "code": "stainless_handrails_with_groove",
        "parent_code": None,
        "name": "Нержавеющие поручни с пазом",
        "sort_order": 14,
    },
    {
        "code": "handrail_tools_consumables",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Инструмент и расходные материалы",
        "sort_order": 1,
    },
    {
        "code": "handrail_components_25_21",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень комплектующие 25*21",
        "sort_order": 2,
    },
    {
        "code": "handrail_components_40_40",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень комплектующие 40*40",
        "sort_order": 3,
    },
    {
        "code": "handrail_components_40_60",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень комплектующие 40*60",
        "sort_order": 4,
    },
    {
        "code": "handrail_components_d42_4",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень комплектующие d42.4",
        "sort_order": 5,
    },
    {
        "code": "handrail_components_d48_3",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень комплектующие d48.3",
        "sort_order": 6,
    },
    {
        "code": "u_shaped_handrail",
        "parent_code": "stainless_handrails_with_groove",
        "name": "Поручень П-образный",
        "sort_order": 7,
    },

    # ============================================
    # 15. НОВИНКИ
    # ============================================
    {
        "code": "new_arrivals",
        "parent_code": None,
        "name": "Новинки",
        "sort_order": 15,
    },
    {
        "code": "sliding_systems",
        "parent_code": "new_arrivals",
        "name": "Раздвижные системы",
        "sort_order": 1,
    },
    {
        "code": "warehouse_equipment",
        "parent_code": "new_arrivals",
        "name": "Складская техника",
        "sort_order": 2,
    },

    # ============================================
    # 16. СПАЙДЕРЫ И ФУРНИТУРА ДЛЯ СТЕКЛЯННЫХ КОЗЫРЬКОВ
    # ============================================
    {
        "code": "spiders_glass_canopy_hardware",
        "parent_code": None,
        "name": "Спайдеры и фурнитура для стеклянных козырьков",
        "sort_order": 16,
    },
    {
        "code": "canopies_ties_m10_aisi316",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Козырьки на тягах М10 AISI 316",
        "sort_order": 1,
    },
    {
        "code": "canopies_ties_m10_aisi304",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Козырьки на тягах М10 AISI 304",
        "sort_order": 2,
    },
    {
        "code": "canopies_aisi316",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Козырьки AISI 316",
        "sort_order": 3,
    },
    {
        "code": "canopy_console",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Консоль для козырьков",
        "sort_order": 4,
    },
    {
        "code": "canopy_fasteners_components",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Крепежи и комплектующие",
        "sort_order": 5,
    },
    {
        "code": "rutels_glass_triplex_glazing",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Рутели для стекла, триплекса и стеклопакетов",
        "sort_order": 6,
    },
    {
        "code": "spiders_for_glass",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "Спайдеры для стекла",
        "sort_order": 7,
    },
    {
        "code": "aisi304_under_tie_m10",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "AISI 304 под тягу М10",
        "sort_order": 8,
    },
    {
        "code": "aisi304_under_tie_m14",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "AISI 304 под тягу М14",
        "sort_order": 9,
    },
    {
        "code": "aisi316_under_tie_m10",
        "parent_code": "spiders_glass_canopy_hardware",
        "name": "AISI 316 под тягу М10",
        "sort_order": 10,
    },

    # ============================================
    # 17. СТЕКЛО И ЗЕРКАЛО
    # ============================================
    {
        "code": "glass_and_mirror",
        "parent_code": None,
        "name": "Стекло и зеркало",
        "sort_order": 17,
    },
    {
        "code": "mirror",
        "parent_code": "glass_and_mirror",
        "name": "Зеркало",
        "sort_order": 1,
    },

    # ============================================
    # 18. СТЕКЛОДЕРЖАТЕЛИ ДЛЯ ОГРАЖДЕНИЙ
    # ============================================
    {
        "code": "glass_holders_for_railings",
        "parent_code": None,
        "name": "Стеклодержатели для ограждений",
        "sort_order": 18,
    },
    {
        "code": "mini_posts_railings",
        "parent_code": "glass_holders_for_railings",
        "name": "Министойки ограждений",
        "sort_order": 1,
    },
    {
        "code": "glass_holders_railings",
        "parent_code": "glass_holders_for_railings",
        "name": "Стеклодержатели для ограждений",
        "sort_order": 2,
    },
    {
        "code": "plate_glass_holder",
        "parent_code": "glass_holders_for_railings",
        "name": "Стеклодержатель пластинчатый",
        "sort_order": 3,
    },
    {
        "code": "end_glass_holder",
        "parent_code": "glass_holders_for_railings",
        "name": "Стеклодержатель торцевой",
        "sort_order": 4,
    },
    {
        "code": "point_fastening_for_glass",
        "parent_code": "glass_holders_for_railings",
        "name": "Точечное крепление для стекла",
        "sort_order": 5,
    },

    # ============================================
    # 19. ТИПОВЫЕ ВАРИАНТЫ СТЕКЛОКОНСТРУКЦИЙ ПОД ЗАКАЗ
    # ============================================
    {
        "code": "typical_custom_glass_structures",
        "parent_code": None,
        "name": "Типовые варианты стеклоконструкций под заказ",
        "sort_order": 19,
    },
    {
        "code": "pendulum_system_vector",
        "parent_code": "typical_custom_glass_structures",
        "name": "Маятниковая система ВЕКТОР",
        "sort_order": 1,
    },
    {
        "code": "pendulum_system_classic",
        "parent_code": "typical_custom_glass_structures",
        "name": "Маятниковая система Классика",
        "sort_order": 2,
    },
    {
        "code": "sliding_system_atlant",
        "parent_code": "typical_custom_glass_structures",
        "name": "Раздвижная система АТЛАНТ",
        "sort_order": 3,
    },
    {
        "code": "sliding_system_harmony",
        "parent_code": "typical_custom_glass_structures",
        "name": "Раздвижная система ГАРМОНИЯ",
        "sort_order": 4,
    },
    {
        "code": "sliding_system_laura",
        "parent_code": "typical_custom_glass_structures",
        "name": "Раздвижная система ЛАУРА",
        "sort_order": 5,
    },
    {
        "code": "sliding_system_002",
        "parent_code": "typical_custom_glass_structures",
        "name": "Раздвижная система серии 002",
        "sort_order": 6,
    },
    {
        "code": "system_vector",
        "parent_code": "typical_custom_glass_structures",
        "name": "Система Вектор",
        "sort_order": 7,
    },
    {
        "code": "glass_interior_doors",
        "parent_code": "typical_custom_glass_structures",
        "name": "Стеклянные межкомнатные двери",
        "sort_order": 8,
    },
    {
        "code": "typical_shower_cabins",
        "parent_code": "typical_custom_glass_structures",
        "name": "Типовые варианты душевых кабин",
        "sort_order": 9,
    },

    # ============================================
    # 20. ТОВАРЫ ПО СПЕЦИАЛЬНОЙ ЦЕНЕ ОТ -30%
    # ============================================
    {
        "code": "special_price_minus_30",
        "parent_code": None,
        "name": "Товары по специальной цене от -30%",
        "sort_order": 20,
    },
    {
        "code": "aluminum_profile",
        "parent_code": "special_price_minus_30",
        "name": "Алюминиевый профиль",
        "sort_order": 1,
    },
    {
        "code": "top_frame_19_19",
        "parent_code": "special_price_minus_30",
        "name": "Верхняя обвязка 19*19",
        "sort_order": 2,
    },
    {
        "code": "top_frame_for_25_pipe",
        "parent_code": "special_price_minus_30",
        "name": "Верхняя обвязка для 25 трубы",
        "sort_order": 3,
    },
    {
        "code": "table_bases",
        "parent_code": "special_price_minus_30",
        "name": "Подстолья для столов",
        "sort_order": 4,
    },
    {
        "code": "handle_for_glass_entrance_doors",
        "parent_code": "special_price_minus_30",
        "name": "Ручка для стеклянных дверей входные группы",
        "sort_order": 5,
    },

    # ============================================
    # 21. ТРУБЫ ИЗ НЕРЖАВЕЮЩЕЙ СТАЛИ
    # ============================================
    {
        "code": "stainless_steel_pipes",
        "parent_code": None,
        "name": "Трубы из нержавеющей стали",
        "sort_order": 21,
    },

    # ============================================
    # 22. УЦЕНЕННЫЕ ТОВАРЫ
    # ============================================
    {
        "code": "discounted_products",
        "parent_code": None,
        "name": "Уцененные товары",
        "sort_order": 22,
    },

    # ============================================
    # 23. ФУРНИТУРА ДЛЯ ЗЕРКАЛ
    # ============================================
    {
        "code": "mirror_hardware",
        "parent_code": None,
        "name": "Фурнитура для зеркал",
        "sort_order": 23,
    },
    {
        "code": "bushings_and_gaskets",
        "parent_code": "mirror_hardware",
        "name": "Втулки и прокладки",
        "sort_order": 1,
    },
    {
        "code": "decorative_plugs",
        "parent_code": "mirror_hardware",
        "name": "Декоративные заглушки",
        "sort_order": 2,
    },
    {
        "code": "protective_film",
        "parent_code": "mirror_hardware",
        "name": "Защитная плёнка",
        "sort_order": 3,
    },
    {
        "code": "mirror_glue",
        "parent_code": "mirror_hardware",
        "name": "Клей для зеркал",
        "sort_order": 4,
    },
    {
        "code": "led_lighting_components",
        "parent_code": "mirror_hardware",
        "name": "Комплектующие для диодной подсветки",
        "sort_order": 5,
    },
    {
        "code": "fastening_without_drilling",
        "parent_code": "mirror_hardware",
        "name": "Крепление без сверления",
        "sort_order": 6,
    },
    {
        "code": "fastening_through_holes",
        "parent_code": "mirror_hardware",
        "name": "Крепление через отверстия",
        "sort_order": 7,
    },
    {
        "code": "mirror_mounts_hangers",
        "parent_code": "mirror_hardware",
        "name": "Крепления зеркал — подвески",
        "sort_order": 8,
    },
    {
        "code": "aluminum_profile_for_mirrors",
        "parent_code": "mirror_hardware",
        "name": "Профиль алюминиевый для зеркал",
        "sort_order": 9,
    },
    {
        "code": "mirror_lamps",
        "parent_code": "mirror_hardware",
        "name": "Светильники для зеркал",
        "sort_order": 10,
    },
    {
        "code": "double_sided_tape",
        "parent_code": "mirror_hardware",
        "name": "Скотч двухсторониий",
        "sort_order": 11,
    },
    {
        "code": "hidden_mirror_fastening",
        "parent_code": "mirror_hardware",
        "name": "Скрытое крепление зеркал",
        "sort_order": 12,
    },

    # ============================================
    # 24. ФУРНИТУРА ДЛЯ ОГРАЖДЕНИЙ (СТЕКЛО — НЕРЖАВЕЙКА)
    # ============================================
    {
        "code": "railing_hardware_glass_stainless",
        "parent_code": None,
        "name": "Фурнитура для ограждений (стекло — нержавейка)",
        "sort_order": 24,
    },
    {
        "code": "ready_railing_posts",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Готовые стойки для ограждений",
        "sort_order": 1,
    },
    {
        "code": "decorative_post_caps",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Декоративные крышки для стоек",
        "sort_order": 2,
    },
    {
        "code": "handrail_holders",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Держатели поручней",
        "sort_order": 3,
    },
    {
        "code": "crossbar_holders",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Держатели ригеля",
        "sort_order": 4,
    },
    {
        "code": "handrail_glass_holder",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Держатель поручня-стекла",
        "sort_order": 5,
    },
    {
        "code": "plugs",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Заглушки",
        "sort_order": 6,
    },
    {
        "code": "post_bases_fasteners",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Низы стоек, крепежи, основания",
        "sort_order": 7,
    },
    {
        "code": "bends_and_connectors",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Отводы и соединители",
        "sort_order": 8,
    },
    {
        "code": "pvc_handrails",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Поручни ПВХ",
        "sort_order": 9,
    },
    {
        "code": "glass_hinges_for_railings",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Стеклопетли для стеклянных ограждений",
        "sort_order": 10,
    },
    {
        "code": "acrylic_railing_posts",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Стойки для перил из акрила",
        "sort_order": 11,
    },
    {
        "code": "tactile_indicators_stainless",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Тактильные индикаторы из нержавеющей стали",
        "sort_order": 12,
    },
    {
        "code": "flanges",
        "parent_code": "railing_hardware_glass_stainless",
        "name": "Фланцы",
        "sort_order": 13,
    },

    # ============================================
    # 25. ФУРНИТУРА ДЛЯ ПЛЕКСИ ПЕРИЛ
    # ============================================
    {
        "code": "plexiglass_railing_hardware",
        "parent_code": None,
        "name": "Фурнитура для плекси перил",
        "sort_order": 25,
    },
    {
        "code": "acrylic_handrails",
        "parent_code": "plexiglass_railing_hardware",
        "name": "Поручни из акрила",
        "sort_order": 1,
    },

    # ============================================
    # 26. ФУРНИТУРА ДЛЯ САУН, БАНИ И ХАМАМ
    # ============================================
    {
        "code": "sauna_bath_hamam_hardware",
        "parent_code": None,
        "name": "Фурнитура для саун, бани и хамам",
        "sort_order": 26,
    },
    {
        "code": "sauna_boxes_profiles",
        "parent_code": "sauna_bath_hamam_hardware",
        "name": "Коробки и профиля для сауны бани парных",
        "sort_order": 1,
    },
    {
        "code": "sauna_bath_hamam_hinges",
        "parent_code": "sauna_bath_hamam_hardware",
        "name": "Петли для сауны бани хамам",
        "sort_order": 2,
    },
    {
        "code": "sauna_bath_handles",
        "parent_code": "sauna_bath_hamam_hardware",
        "name": "Ручки для бани сауны парной",
        "sort_order": 3,
    },
]