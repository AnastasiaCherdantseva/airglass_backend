"""
Скрипт для создания пользователя с ролью.

Запуск:
    cd backend
    source .venv/Scripts/activate
    python scripts/create_user.py
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.system import User, Role, UserRole
from app.core.security import hash_password

# ============================================
# ДАННЫЕ ДЛЯ СОЗДАНИЯ
# ============================================

ROLE_ID = uuid.UUID("6ea3b69d-eb73-45f8-81bd-a5a114ac59ca")
USER_NAME = "Разработчик"
USER_EMAIL = "developer@airglass.ru"
USER_PASSWORD = "123"  # ← временный пароль
IS_ACTIVE = True


async def create_user():
    async with AsyncSessionLocal() as db:
        # 1. Проверить роль
        role = await db.get(Role, ROLE_ID)
        if not role:
            print(f"❌ Роль с id={ROLE_ID} не найдена")
            return
        print(f"✅ Роль найдена: {role.code} ({role.name})")

        # 2. Проверить email
        existing = await db.execute(
            select(User).where(User.email == USER_EMAIL)
        )
        if existing.scalar_one_or_none():
            print(f"❌ Пользователь с email={USER_EMAIL} уже существует")
            return
        print(f"✅ Email свободен: {USER_EMAIL}")

        # 3. Хешировать пароль
        password_hash = hash_password(USER_PASSWORD)
        print(f"✅ Пароль захеширован")

        # 4. Создать пользователя
        user = User(
            id=uuid.uuid4(),
            name=USER_NAME,
            email=USER_EMAIL,
            password_hash=password_hash,
            is_active=IS_ACTIVE,
        )
        db.add(user)
        await db.flush()
        print(f"✅ Пользователь создан: {user.id}")

        # 5. Привязать роль
        user_role = UserRole(
            user_id=user.id,
            role_id=ROLE_ID,
        )
        db.add(user_role)

        # 6. Сохранить
        await db.commit()
        await db.refresh(user)

        print(f"\n✅ ГОТОВО!")
        print(f"   ID:       {user.id}")
        print(f"   Имя:      {user.name}")
        print(f"   Email:    {user.email}")
        print(f"   Активен:  {user.is_active}")
        print(f"   Роль:     {role.code} ({role.name})")
        print(f"   Пароль:   {USER_PASSWORD}")



if __name__ == "__main__":
    asyncio.run(create_user())