# from typing import Optional


from pydantic import Field

from app.schemas.base import BaseSchema, Email


class AuthLoginRequest(BaseSchema):
    # Запрос
    email: Email = Field(min_length=6, max_length=255)
    password: str = Field(min_length=6, max_length=100)
    user_agent: str | None = None
    ip_address: str | None = None
