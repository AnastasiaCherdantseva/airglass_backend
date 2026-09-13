"""
Seed-данные: связь ролей с правами.

Ключ — код роли, значение — список кодов прав.
`"*"` означает «все права из PERMISSIONS».
"""

ROLE_PERMISSIONS = {
    # ==========================================
    # SYSTEM_ADMIN — все права
    # ==========================================
    "SYSTEM_ADMIN": ["*"],

    # ==========================================
    # MANAGER — продажи, клиенты, КП, проекты
    # ==========================================
    "MANAGER": [
        "calculator.read.all",
        "customers.create.all",
        "customers.read.all",
        "quotes.create.all",
        "quotes.read.all",
        "quotes.update.own",
        "quotes.delete.own",
        "projects.create.all",
        "projects.read.all",
        "projects.update.all",
        "products.read.all",
        "templates.read.all",
        "suppliers.manage.all",
    ],

    # ==========================================
    # ENGINEER — каталог, шаблоны, расчёты
    # ==========================================
    "ENGINEER": [
        "calculator.read.all",
        "products.create.all",
        "products.read.all",
        "products.update.all",
        "templates.create.all",
        "templates.read.all",
        "templates.update.all",
        "templates.delete.own",
        "projects.read.all",
        "projects.update.all",
        "customers.read.all",
    ],

    # ==========================================
    # VIEWER — только чтение
    # ==========================================
    "VIEWER": [
        "calculator.read.all",
        "products.read.all",
        "templates.read.all",
        "quotes.read.all",
        "projects.read.all",
        "customers.read.all",
    ],
}