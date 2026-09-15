"""
Базовые схемы и общие валидаторы.
"""

import re
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict, BeforeValidator


# ============================================
# EMAIL REGEX
# ============================================

# ✅ Поддерживает:
# - латиницу: user@mail.ru
# - кириллицу: пользователь@mail.ру
# - IDN-домены: mail.рф, mail.укр
# - плюс-теги: user+tag@mail.ru
# - поддомены: user@sub.mail.ru
#
# Требует:
# - @ в середине
# - домен с точкой
# - TLD 2+ символа

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9а-яА-ЯёЁ._%+-]+"          # ← имя пользователя (латиница + кириллица)
    r"@"
    r"[a-zA-Z0-9а-яА-ЯёЁ.-]+"               # ← домен (латиница + кириллица)
    r"\."
    r"[a-zA-Zа-яА-ЯёЁ]{2,}$"                # ← TLD (2+ символа)
)


def validate_email(value: str) -> str:
    """
    Проверить email.
    
    Поддерживает кириллицу в имени и домене.
    Требует TLD (2+ символа).
    """
    if not isinstance(value, str):
        raise ValueError("Email должен быть строкой")
    
    value = value.strip().lower()
    
    if not value:
        raise ValueError("Email не может быть пустым")
    
    if len(value) > 254:
        raise ValueError("Email слишком длинный (максимум 254 символа)")
    
    if not EMAIL_REGEX.match(value):
        raise ValueError(
            "Неверный формат email. "
            "Пример: user@mail.ru или пользователь@mail.рф"
        )
    
    # Дополнительные проверки
    local_part, domain = value.rsplit("@", 1)
    
    if len(local_part) > 64:
        raise ValueError("Имя пользователя слишком длинное (максимум 64 символа)")
    
    if ".." in value:
        raise ValueError("Email не может содержать две точки подряд")
    
    if value.startswith(".") or value.startswith("@"):
        raise ValueError("Email не может начинаться с точки или @")
    
    if value.endswith(".") or value.endswith("@"):
        raise ValueError("Email не может заканчиваться точкой или @")
    
    return value


# ============================================
# ТИПЫ
# ============================================

Email = Annotated[str, BeforeValidator(validate_email)]


# ============================================
# БАЗОВАЯ СХЕМА
# ============================================

class BaseSchema(BaseModel):
    """Базовая схема с общими настройками."""
    
    model_config = ConfigDict(
        from_attributes=True,       # ← для ORM
        str_strip_whitespace=True,  # ← удалять пробелы
        validate_assignment=True,   # ← валидация при изменении
    )