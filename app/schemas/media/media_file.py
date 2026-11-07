from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class MediaFileResponse(BaseSchema):
    id: UUID
    storage_key: str
    original_filename: str
    mime_type: str
    file_size: int
    width: int | None
    height: int | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
