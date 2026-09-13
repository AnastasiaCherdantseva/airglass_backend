"""
Seed-данные для цветов.

Все цвета приведены к единому формату:
    {
        "code": str,          # уникальный код
        "name": str,          # человекочитаемое имя
        "hex_color": str,     # HEX-цвет
        "group_code": str,    # код группы (FURNITURE / GLASS / RAL)
        "sort_order": int,    # порядок сортировки
    }
"""

# ============================================
# ФУРНИТУРА
# ============================================
FURNITURE_COLORS = [
    {"code": "chrome",         "name": "Хром",         "hex_color": "#C0C0C0", "group_code": "FURNITURE", "sort_order": 1},
    {"code": "matte_chrome",   "name": "Матовый хром", "hex_color": "#A9A9A9", "group_code": "FURNITURE", "sort_order": 2},
    {"code": "gold",           "name": "Золото",       "hex_color": "#FFD700", "group_code": "FURNITURE", "sort_order": 3},
    {"code": "bronze",         "name": "Бронза",       "hex_color": "#CD7F32", "group_code": "FURNITURE", "sort_order": 4},
    {"code": "black_furniture","name": "Чёрный",       "hex_color": "#000000", "group_code": "FURNITURE", "sort_order": 5},
]


# ============================================
# СТЕКЛО
# ============================================
GLASS_COLORS = [
    {
        "code": "transparent_M1",
        "name": "Прозрачное М1",
        "hex_color": "#E8F4F8",
        "group_code": "GLASS",
        "sort_order": 1,
    },
    {
        "code": "tinted_gray",
        "name": "Тонированное (серое)",
        "hex_color": "#6B7075",
        "group_code": "GLASS",
        "sort_order": 2,
    },
    {
        "code": "tinted_bronze",
        "name": "Тонированное (бронза)",
        "hex_color": "#80624A",
        "group_code": "GLASS",
        "sort_order": 3,
    },
    {
        "code": "lightened",
        "name": "Осветлённое",
        "hex_color": "#F0F8FF",
        "group_code": "GLASS",
        "sort_order": 4,
    },
    {
        "code": "matte",
        "name": "Матовое",
        "hex_color": "#E5E5E5",
        "group_code": "GLASS",
        "sort_order": 5,
    },
]


# ============================================
# RAL
# ============================================
RAL_COLORS = [
    # ------------------------------------------
    # ЖЁЛТЫЕ (Yellow)
    # ------------------------------------------
    {"code": "RAL1000", "name": "Зелено-бежевый",          "hex_color": "#CDBA88", "group_code": "RAL", "sort_order": 1},
    {"code": "RAL1001", "name": "Бежевый",                 "hex_color": "#D0B084", "group_code": "RAL", "sort_order": 2},
    {"code": "RAL1002", "name": "Песочно-желтый",          "hex_color": "#D2AA6D", "group_code": "RAL", "sort_order": 3},
    {"code": "RAL1013", "name": "Жемчужно-белый",          "hex_color": "#E3D9C6", "group_code": "RAL", "sort_order": 4},
    {"code": "RAL1015", "name": "Светлая слоновая кость",  "hex_color": "#E6D2B5", "group_code": "RAL", "sort_order": 5},
    {"code": "RAL1021", "name": "Рапсово-жёлтый",          "hex_color": "#F6B600", "group_code": "RAL", "sort_order": 6},
    {"code": "RAL1023", "name": "Транспортно-жёлтый",      "hex_color": "#F7B500", "group_code": "RAL", "sort_order": 7},

    # ------------------------------------------
    # ОРАНЖЕВЫЕ (Orange)
    # ------------------------------------------
    {"code": "RAL2000", "name": "Жёлто-оранжевый",         "hex_color": "#ED760E", "group_code": "RAL", "sort_order": 8},
    {"code": "RAL2003", "name": "Пастельно-оранжевый",     "hex_color": "#FF7514", "group_code": "RAL", "sort_order": 9},
    {"code": "RAL2004", "name": "Оранжевый",               "hex_color": "#F44611", "group_code": "RAL", "sort_order": 10},
    {"code": "RAL2010", "name": "Сигнальный оранжевый",    "hex_color": "#D84B20", "group_code": "RAL", "sort_order": 11},
    {"code": "RAL2012", "name": "Лососёво-оранжевый",      "hex_color": "#E55137", "group_code": "RAL", "sort_order": 12},

    # ------------------------------------------
    # КРАСНЫЕ (Red)
    # ------------------------------------------
    {"code": "RAL3000", "name": "Огненно-красный",         "hex_color": "#AF2B1E", "group_code": "RAL", "sort_order": 13},
    {"code": "RAL3001", "name": "Сигнальный красный",      "hex_color": "#A52019", "group_code": "RAL", "sort_order": 14},
    {"code": "RAL3003", "name": "Рубиново-красный",        "hex_color": "#9B111E", "group_code": "RAL", "sort_order": 15},
    {"code": "RAL3004", "name": "Пурпурно-красный",        "hex_color": "#75151E", "group_code": "RAL", "sort_order": 16},
    {"code": "RAL3005", "name": "Винно-красный",           "hex_color": "#5E2129", "group_code": "RAL", "sort_order": 17},
    {"code": "RAL3009", "name": "Оксид красный",           "hex_color": "#642424", "group_code": "RAL", "sort_order": 18},
    {"code": "RAL3011", "name": "Коричнево-красный",       "hex_color": "#781F19", "group_code": "RAL", "sort_order": 19},
    {"code": "RAL3020", "name": "Транспортный красный",    "hex_color": "#CC0605", "group_code": "RAL", "sort_order": 20},

    # ------------------------------------------
    # ФИОЛЕТОВЫЕ (Violet)
    # ------------------------------------------
    {"code": "RAL4005", "name": "Сине-сиреневый",          "hex_color": "#6C4675", "group_code": "RAL", "sort_order": 21},
    {"code": "RAL4008", "name": "Сигнальный фиолетовый",   "hex_color": "#924E7D", "group_code": "RAL", "sort_order": 22},

    # ------------------------------------------
    # СИНИЕ (Blue)
    # ------------------------------------------
    {"code": "RAL5000", "name": "Фиолетово-синий",         "hex_color": "#354D73", "group_code": "RAL", "sort_order": 23},
    {"code": "RAL5002", "name": "Ультрамариново-синий",    "hex_color": "#20214F", "group_code": "RAL", "sort_order": 24},
    {"code": "RAL5005", "name": "Сигнальный синий",        "hex_color": "#1E2460", "group_code": "RAL", "sort_order": 25},
    {"code": "RAL5010", "name": "Горечавково-синий",       "hex_color": "#0E294B", "group_code": "RAL", "sort_order": 26},
    {"code": "RAL5011", "name": "Стально-синий",           "hex_color": "#231A24", "group_code": "RAL", "sort_order": 27},
    {"code": "RAL5015", "name": "Небесно-синий",           "hex_color": "#1B75B7", "group_code": "RAL", "sort_order": 28},
    {"code": "RAL5017", "name": "Транспортный синий",      "hex_color": "#0F4C91", "group_code": "RAL", "sort_order": 29},
    {"code": "RAL5024", "name": "Пастельно-синий",         "hex_color": "#5D9B9B", "group_code": "RAL", "sort_order": 30},

    # ------------------------------------------
    # ЗЕЛЁНЫЕ (Green)
    # ------------------------------------------
    {"code": "RAL6000", "name": "Патиново-зелёный",        "hex_color": "#316650", "group_code": "RAL", "sort_order": 31},
    {"code": "RAL6001", "name": "Изумрудно-зелёный",       "hex_color": "#2B5C38", "group_code": "RAL", "sort_order": 32},
    {"code": "RAL6002", "name": "Лиственно-зелёный",       "hex_color": "#2D572C", "group_code": "RAL", "sort_order": 33},
    {"code": "RAL6003", "name": "Оливково-зелёный",        "hex_color": "#424632", "group_code": "RAL", "sort_order": 34},
    {"code": "RAL6005", "name": "Зелёный мох",             "hex_color": "#2F4C2F", "group_code": "RAL", "sort_order": 35},
    {"code": "RAL6009", "name": "Пихтовый зелёный",        "hex_color": "#2D3632", "group_code": "RAL", "sort_order": 36},
    {"code": "RAL6011", "name": "Резедово-зелёный",        "hex_color": "#5F7D50", "group_code": "RAL", "sort_order": 37},
    {"code": "RAL6018", "name": "Желто-зелёный",           "hex_color": "#5B9C2D", "group_code": "RAL", "sort_order": 38},
    {"code": "RAL6021", "name": "Бледно-зелёный",          "hex_color": "#7E8B5A", "group_code": "RAL", "sort_order": 39},
    {"code": "RAL6029", "name": "Мятно-зелёный",           "hex_color": "#006B3E", "group_code": "RAL", "sort_order": 40},

    # ------------------------------------------
    # СЕРЫЕ (Grey) — самые ходовые
    # ------------------------------------------
    {"code": "RAL7000", "name": "Серая белка",             "hex_color": "#78858B", "group_code": "RAL", "sort_order": 41},
    {"code": "RAL7001", "name": "Серебристо-серый",        "hex_color": "#8A9597", "group_code": "RAL", "sort_order": 42},
    {"code": "RAL7004", "name": "Сигнальный серый",        "hex_color": "#969992", "group_code": "RAL", "sort_order": 43},
    {"code": "RAL7011", "name": "Железно-серый",           "hex_color": "#434B4D", "group_code": "RAL", "sort_order": 44},
    {"code": "RAL7012", "name": "Базальтово-серый",        "hex_color": "#4E5754", "group_code": "RAL", "sort_order": 45},
    {"code": "RAL7015", "name": "Сланцево-серый",          "hex_color": "#434750", "group_code": "RAL", "sort_order": 46},
    {"code": "RAL7016", "name": "Антрацитово-серый",       "hex_color": "#293133", "group_code": "RAL", "sort_order": 47},
    {"code": "RAL7021", "name": "Чёрно-серый",             "hex_color": "#23282B", "group_code": "RAL", "sort_order": 48},
    {"code": "RAL7024", "name": "Графитово-серый",         "hex_color": "#474A51", "group_code": "RAL", "sort_order": 49},
    {"code": "RAL7035", "name": "Светло-серый",            "hex_color": "#D7D7D7", "group_code": "RAL", "sort_order": 50},
    {"code": "RAL7037", "name": "Пыльно-серый",            "hex_color": "#7D7F7D", "group_code": "RAL", "sort_order": 51},
    {"code": "RAL7039", "name": "Кварцево-серый",          "hex_color": "#6C6960", "group_code": "RAL", "sort_order": 52},
    {"code": "RAL7040", "name": "Оконно-серый",            "hex_color": "#9DA1AA", "group_code": "RAL", "sort_order": 53},
    {"code": "RAL7042", "name": "Транспортный серый A",    "hex_color": "#8D948D", "group_code": "RAL", "sort_order": 54},

    # ------------------------------------------
    # КОРИЧНЕВЫЕ (Brown)
    # ------------------------------------------
    {"code": "RAL8003", "name": "Глиняно-коричневый",      "hex_color": "#734222", "group_code": "RAL", "sort_order": 55},
    {"code": "RAL8004", "name": "Медно-коричневый",        "hex_color": "#8E402A", "group_code": "RAL", "sort_order": 56},
    {"code": "RAL8011", "name": "Орехово-коричневый",      "hex_color": "#5B3A29", "group_code": "RAL", "sort_order": 57},
    {"code": "RAL8014", "name": "Сепия коричневая",        "hex_color": "#382C1E", "group_code": "RAL", "sort_order": 58},
    {"code": "RAL8016", "name": "Махагон коричневый",      "hex_color": "#4C2F27", "group_code": "RAL", "sort_order": 59},
    {"code": "RAL8017", "name": "Шоколадно-коричневый",    "hex_color": "#45322E", "group_code": "RAL", "sort_order": 60},
    {"code": "RAL8019", "name": "Серо-коричневый",         "hex_color": "#403A3A", "group_code": "RAL", "sort_order": 61},

    # ------------------------------------------
    # БЕЛЫЕ И ЧЁРНЫЕ (White and Black)
    # ------------------------------------------
    {"code": "RAL9001", "name": "Кремово-белый",           "hex_color": "#FDF4E3", "group_code": "RAL", "sort_order": 62},
    {"code": "RAL9002", "name": "Серо-белый",              "hex_color": "#E7EBDA", "group_code": "RAL", "sort_order": 63},
    {"code": "RAL9003", "name": "Сигнальный белый",        "hex_color": "#F4F4F4", "group_code": "RAL", "sort_order": 64},
    {"code": "RAL9004", "name": "Сигнальный чёрный",       "hex_color": "#282828", "group_code": "RAL", "sort_order": 65},
    {"code": "RAL9005", "name": "Чёрный",                  "hex_color": "#0A0A0A", "group_code": "RAL", "sort_order": 66},
    {"code": "RAL9006", "name": "Бело-алюминиевый",        "hex_color": "#A5A5A5", "group_code": "RAL", "sort_order": 67},
    {"code": "RAL9007", "name": "Серо-алюминиевый",        "hex_color": "#8F8F8F", "group_code": "RAL", "sort_order": 68},
    {"code": "RAL9010", "name": "Чисто-белый",             "hex_color": "#FFFFFF", "group_code": "RAL", "sort_order": 69},
    {"code": "RAL9011", "name": "Графитно-чёрный",         "hex_color": "#1C1C1C", "group_code": "RAL", "sort_order": 70},
    {"code": "RAL9016", "name": "Транспортный белый",      "hex_color": "#F1F1F1", "group_code": "RAL", "sort_order": 71},
    {"code": "RAL9017", "name": "Транспортный чёрный",     "hex_color": "#1E1E1E", "group_code": "RAL", "sort_order": 72},
    {"code": "RAL9018", "name": "Папирусно-белый",         "hex_color": "#D7D7D7", "group_code": "RAL", "sort_order": 73},
]


# ============================================
# ОБЩИЙ СПИСОК
# ============================================
ALL_COLORS = FURNITURE_COLORS + GLASS_COLORS + RAL_COLORS