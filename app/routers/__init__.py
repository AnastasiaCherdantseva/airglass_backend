"""
Сборка всех роутеров в один api_router.
"""

from fastapi import APIRouter

from app.routers.v1.catalog.category import router as category_router
from app.routers.v1.catalog.unit import router as unit_router
from app.routers.v1.system.auth import router as auth_router
from app.routers.v1.system.organization import router as organization_router
from app.routers.v1.system.role import router as role_router
from app.routers.v1.system.user import router as user_router
from app.routers.v1.usage.usage_roles import router as usege_role_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(organization_router)
api_router.include_router(category_router)
api_router.include_router(usege_role_router)
api_router.include_router(unit_router)

__all__ = ["api_router"]
