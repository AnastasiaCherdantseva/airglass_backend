from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.dto.media.media_file import MediaFileOutput


@dataclass(frozen=True)
class CategoryOutput:
    id: UUID
    parent_id: UUID | None
    name: str
    code: str
    description: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    attributes_ids: list[UUID]
    media_data: MediaFileOutput | None


@dataclass(frozen=True)
class CategoryWithRulesOutput(CategoryOutput):
    usage_role_ids: list[UUID]
