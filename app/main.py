"""
Точка входа FastAPI.
- lifespan: запуск/остановка планировщика задач (APScheduler).
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.jobs.cleanup_sessions import cleanup_expired_sessions
from app.routers import api_router
from app.routers.errors import register_exception_handlers

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _cleanup_job() -> None:
    """Scheduled wrapper for cleanup_expired_sessions."""
    await cleanup_expired_sessions()


def register_jobs() -> None:
    """Register all scheduled jobs."""
    scheduler.add_job(
        _cleanup_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_sessions",
        replace_existing=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.RUN_CRON and not scheduler.running:
        register_jobs()
        scheduler.start()
        logger.info("Scheduler started")
    yield
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


app = FastAPI(title="Airglass Backend", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "db": str(e)}
