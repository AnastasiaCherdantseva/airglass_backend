from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # ← добавили для безопасного выполнения SQL
from app.core.db import get_db, engine, Base

# Создаём таблицы (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Airglass Backend")

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