import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем URL базы данных из переменных окружения

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "localhost")   # по умолчанию localhost
DB_PORT = os.getenv("DB_PORT", "5432")        # по умолчанию 5432

# Проверка, что все переменные заданы
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Не все переменные окружения для БД заданы!")

# Собираем URL
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Создаём движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,  # уже содержит asyncpg
    echo=True,
    pool_size=5,
    max_overflow=10
)
# Создаём фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД (для Dependency Injection в FastAPI)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session