# from typing import Optional

from pydantic import Field

# from decimal import Decimal
from app.schemas.base import BaseSchema, Email


class AuthBase(BaseSchema):
    email: Email = Field(min_length=6, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
