import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models import (
        Project,
        QuoteVersion,
        GeneratedDocument,
    )


class QuoteStatus(str, enum.Enum):
    """Статусы коммерческого предложения"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class Quote(Base, TimestampMixin, SoftDeleteMixin):
    """
    Коммерческое предложение.

    Это контейнер для версий КП.
    """
    __tablename__ = "quotes"
    __table_args__ = (
        Index("ix_quote_project_id", "project_id"),
        Index("ix_quote_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
    )
    number: Mapped[str] = mapped_column(String(50))
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus),
        default=QuoteStatus.DRAFT,
        server_default=text("'DRAFT'"),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    # Связи
    project: Mapped["Project"] = relationship(back_populates="quotes")
    versions: Mapped[list["QuoteVersion"]] = relationship(
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteVersion.version_number",
    )
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship(
        back_populates="quote",
    )

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def latest_version(self) -> "QuoteVersion | None":
        """Последняя версия КП"""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)

    @property
    def current_version(self) -> "QuoteVersion | None":
        """Текущая (последняя) версия"""
        return self.latest_version

    @property
    def versions_count(self) -> int:
        """Количество версий"""
        return len(self.versions)

    @property
    def is_approved(self) -> bool:
        """Утверждено ли КП"""
        return self.status == QuoteStatus.APPROVED

    @property
    def can_be_edited(self) -> bool:
        """Можно ли редактировать КП"""
        return self.status in (QuoteStatus.DRAFT, QuoteStatus.SENT)