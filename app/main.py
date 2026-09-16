from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # ← добавили для безопасного выполнения SQL

from backend.app.core.database import get_db, engine
from backend.app.models.base import Base
from backend.app.routers.errors import register_exception_handlers
from backend.app.routers import api_router

# Создаём таблицы (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Airglass Backend")
app.include_router(api_router, prefix="/api")

register_exception_handlers(app)


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        # Используем text() для безопасного выполнения raw SQL
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}