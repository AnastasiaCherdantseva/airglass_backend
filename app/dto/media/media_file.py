from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class MediaFileOutput:
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
