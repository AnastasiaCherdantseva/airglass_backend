from datetime import UTC, datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TimestampMixin:
    """Миксин для created_at / updated_at."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            server_default=text("now()"),
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
            server_default=text("now()"),
        )


class SoftDeleteMixin:
    """Миксин для мягкого удаления."""

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True))

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
