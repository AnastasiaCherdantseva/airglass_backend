"""
Seed-данные для прав.
"""

PERMISSIONS = [
    # ============================================
    # CALCULATOR
    # ============================================
    {
        "code": "calculator.read.all",
        "name": "Доступ к калькулятору",
        "resource": "calculator",
        "action": "read",
        "scope": "all",
    },
    
    # ============================================
    # USERS
    # ============================================
    {
        "code": "users.create.all",
        "name": "Создание пользователей",
        "resource": "users",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "users.read.all",
        "name": "Просмотр пользователей",
        "resource": "users",
        "action": "read",
        "scope": "all",
    },
    {
        "code": "users.update.all",
        "name": "Редактирование пользователей",
        "resource": "users",
        "action": "update",
        "scope": "all",
    },
    {
        "code": "users.delete.all",
        "name": "Удаление пользователей",
        "resource": "users",
        "action": "delete",
        "scope": "all",
    },
    
    # ============================================
    # ROLES
    # ============================================
    {
        "code": "roles.manage.all",
        "name": "Управление ролями",
        "resource": "roles",
        "action": "manage",
        "scope": "all",
    },
    
    # ============================================
    # PRODUCTS
    # ============================================
    {
        "code": "products.create.all",
        "name": "Создание товаров",
        "resource": "products",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "products.read.all",
        "name": "Просмотр товаров",
        "resource": "products",
        "action": "read",
        "scope": "all",
    },
    {
        "code": "products.update.all",
        "name": "Редактирование товаров",
        "resource": "products",
        "action": "update",
        "scope": "all",
    },
    {
        "code": "products.delete.all",
        "name": "Удаление товаров",
        "resource": "products",
        "action": "delete",
        "scope": "all",
    },
    
    # ============================================
    # TEMPLATES
    # ============================================
    {
        "code": "templates.create.all",
        "name": "Создание шаблонов",
        "resource": "templates",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "templates.read.all",
        "name": "Просмотр шаблонов",
        "resource": "templates",
        "action": "read",
        "scope": "all",
    },
    {
        "code": "templates.update.all",
        "name": "Редактирование шаблонов",
        "resource": "templates",
        "action": "update",
        "scope": "all",
    },
    {
        "code": "templates.delete.own",
        "name": "Удаление своих шаблонов",
        "resource": "templates",
        "action": "delete",
        "scope": "own",
    },
    
    # ============================================
    # QUOTES
    # ============================================
    {
        "code": "quotes.create.all",
        "name": "Создание КП",
        "resource": "quotes",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "quotes.read.all",
        "name": "Просмотр КП",
        "resource": "quotes",
        "action": "read",
        "scope": "all",
    },
    {
        "code": "quotes.update.own",
        "name": "Редактирование своих КП",
        "resource": "quotes",
        "action": "update",
        "scope": "own",
    },
    {
        "code": "quotes.delete.own",
        "name": "Удаление своих КП",
        "resource": "quotes",
        "action": "delete",
        "scope": "own",
    },
    {
        "code": "quotes.approve.all",
        "name": "Утверждение КП",
        "resource": "quotes",
        "action": "approve",
        "scope": "all",
    },
    
    # ============================================
    # PROJECTS
    # ============================================
    {
        "code": "projects.create.all",
        "name": "Создание проектов",
        "resource": "projects",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "projects.read.all",
        "name": "Просмотр проектов",
        "resource": "projects",
        "action": "read",
        "scope": "all",
    },
    {
        "code": "projects.update.all",
        "name": "Редактирование проектов",
        "resource": "projects",
        "action": "update",
        "scope": "all",
    },
    
    # ============================================
    # CUSTOMERS
    # ============================================
    {
        "code": "customers.create.all",
        "name": "Создание заказчиков",
        "resource": "customers",
        "action": "create",
        "scope": "all",
    },
    {
        "code": "customers.read.all",
        "name": "Просмотр заказчиков",
        "resource": "customers",
        "action": "read",
        "scope": "all",
    },
    
    # ============================================
    # SUPPLIERS
    # ============================================
    {
        "code": "suppliers.manage.all",
        "name": "Управление поставщиками",
        "resource": "suppliers",
        "action": "manage",
        "scope": "all",
    },
    
    # ============================================
    # SETTINGS
    # ============================================
    {
        "code": "settings.manage.all",
        "name": "Управление настройками",
        "resource": "settings",
        "action": "manage",
        "scope": "all",
    },
    
    # ============================================
    # AUDIT LOG
    # ============================================
    {
        "code": "audit_log.read.all",
        "name": "Просмотр логов",
        "resource": "audit_log",
        "action": "read",
        "scope": "all",
    },
]