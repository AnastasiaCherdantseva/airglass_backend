"""
Сборка всех роутеров в один api_router.
"""

from fastapi import APIRouter

from app.routers.v1.system.auth import router as auth_router
from app.routers.v1.system.organization import router as organization_router
from app.routers.v1.system.user import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(organization_router)

__all__ = ["api_router"]
