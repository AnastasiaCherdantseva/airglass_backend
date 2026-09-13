from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean, text
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    """Миксин для created_at / updated_at"""

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
            server_default=text("now()"),
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
            server_default=text("now()")
        )


class SoftDeleteMixin:
    """Миксин для мягкого удаления"""

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None