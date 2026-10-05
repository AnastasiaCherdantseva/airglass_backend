"""
Users router.

Роутер пользователей.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Пользователи"])

# Коды прав
USERS_CREATE = "USERS.CREATE"
