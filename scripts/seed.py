"""
Скрипт для загрузки seed-данных.

Запуск:
    cd backend
    source .venv/Scripts/activate
    python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Добавить корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.db.seed import seed_all


async def main():
    """Загрузить все seed-данные."""
    async with AsyncSessionLocal() as db:
        await seed_all(db)


if __name__ == "__main__":
    asyncio.run(main())