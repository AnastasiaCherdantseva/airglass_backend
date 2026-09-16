"""
Сборка всех роутеров в один api_router.
"""

from fastapi import APIRouter

# from app.routers.users import router as users_router
# from app.routers.roles import router as roles_router

api_router = APIRouter()

# api_router.include_router(users_router)
# api_router.include_router(roles_router)

__all__ = ["api_router"]