# Airglass — проект

## 1. Общее

**Продукт:** Airglass — веб-B2B-приложение для управления полным
жизненным циклом заказов стекольных ограждений.
**Рабочее имя локальной папки:** `new_calculator`.
**Архитектура:** два независимых репозитория — `backend` и `frontend`.
Связь — через HTTP API. Общий `.env` в корне.
**Стиль:** чистая архитектура, SRP. Бизнес-логика не живёт в роутерах.

## 2. Корень проекта (локально)

new_calculator/
├── .vscode/
├── backend/
├── frontend/
├── .env # общий для обоих проектов
├── dev.sh
├── docker-compose.yml
└── docker-compose.prod.yml

## 3. Backend

### 3.1. Стек
- Python 3.11+, FastAPI 0.104, SQLAlchemy 2.0 (async), asyncpg
- Pydantic v2 + pydantic-settings
- Alembic (миграции)
- APScheduler (фоновые задачи)
- pwdlib[bcrypt] (хеширование паролей)
- Полный список — в `pyproject.toml`

### Что важно помнить
- Хеширование (всего - паролейб токенов и тд) — только в use case.
  Репозиторий принимает готовый хеш, не делает хеширование сам.

### 3.2. Дерево

backend/
├── alembic/
│ └── versions/
├── app/
│ ├── core/ # конфиг, БД, UoW, security
│ ├── db/
│ │ └── seed/ # seed-данные
│ ├── jobs/ # фоновые задачи (APScheduler)
│ ├── models/ # SQLAlchemy-модели
│ │ ├── access/ # Permission, PermissionCondition, Role, ...
│ │ └── system/ # User, Session, Role, ...
│ ├── repositories/ # доступ к данным + protocol-контракты
│ │ ├── protocols/ # протоколы репозиториев
│ │ ├── base.py # BaseIdRepository, протоколы
│ │ ├── dependencies.py # get_uow, get_<entity>_repo
│ │ └── system/ # реализации репозиториев
│ ├── routers/ # FastAPI-роутеры
│ ├── schemas/ # Pydantic-схемы
│ └── use_cases/ # бизнес-логика
├── docs/
│ ├── business-rules.md
│ ├── decisions.md
│ └── project-structure.md
├── scripts/
│ ├── seed.py # запуск сидирования
│ └── ...
├── tests/
│ ├── integration/
│ └── unit/
├── main.py # точка входа
└── pyproject.toml

### 3.3. Назначение слоёв

| Слой | Отвечает за | Не должен |
|---|---|---|
| `routers/` | HTTP: приём, валидация, вызов use case, ответ | Содержать бизнес-логику |
| `use_cases/` | Бизнес-логика, оркестрация репозиториев | Знать про HTTP |
| `repositories/` | Доступ к БД | Знать про HTTP и use case |
| `models/` | SQLAlchemy-модели | Содержать логику |
| `schemas/` | Pydantic-схемы | Содержать логику |
| `core/` | Конфиг, сессия БД, UoW, security | Бизнес-логика |
| `jobs/` | Периодические задачи | Прямой доступ к HTTP |
| `db/seed/` | Заполнение справочников | Бизнес-логика |

### 3.4. Unit of Work

Репозитории **не инстанцируются напрямую** в роутерах. Доступ — через
фабричные функции в `repositories/dependencies.py`:

- `get_uow()` — открывает `AsyncSession`, оборачивает в `UnitOfWork`,
  commit при успехе / rollback при исключении.
- `get_<entity>_repo(uow=Depends(get_uow))` — возвращает репозиторий,
  привязанный к сессии из UoW.

```python
async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with AsyncSessionLocal() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
        except Exception:
            await uow.rollback()
            raise
        else:
            await uow.commit()
```