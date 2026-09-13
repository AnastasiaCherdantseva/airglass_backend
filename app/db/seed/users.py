"""
Seed-данные для начального пользователя-администратора.

Пароль хэшируется при загрузке через app.core.security.hash_password.

Значения по умолчанию можно переопределить через переменные окружения:
    SEED_ADMIN_EMAIL
    SEED_ADMIN_PASSWORD
    SEED_ADMIN_NAME
"""

import os

# Значения по умолчанию — для dev-стенда.
# На проде задавайте через переменные окружения.
SEED_ADMIN = {
    "name": os.environ.get("SEED_ADMIN_NAME", "Разработчик"),
    "email": os.environ.get("SEED_ADMIN_EMAIL", "dev@example.com"),
    "password": os.environ.get("SEED_ADMIN_PASSWORD", "admin123"),
    "role_code": "SYSTEM_ADMIN",
    "is_active": True,
}