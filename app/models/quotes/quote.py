import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class QuoteStatus(str, enum.Enum):
    """Статусы коммерческого предложения"""
    DRAFT = "DRAFT"          # черновик
    SENT = "SENT"            # отправлено клиенту
    APPROVED = "APPROVED"    # клиент согласился
    REJECTED = "REJECTED"    # клиент отказался
    ARCHIVED = "ARCHIVED"    # в архиве


class Quote(Base, TimestampMixin, SoftDeleteMixin):
    """
    Коммерческое предложение.
    
    Это контейнер для версий КП.
    Один проект может иметь несколько КП.
    Одно КП может иметь несколько версий.
    
    Пример:
        Project "Душевая в ЖК Северный"
            ├── Quote №1 "Базовый вариант"
            │   ├── QuoteVersion v1
            │   ├── QuoteVersion v2
            │   └── QuoteVersion v3
            └── Quote №2 "Премиум вариант"
                └── QuoteVersion v1
    """
    __tablename__ = "quotes"
    __table_args__ = (
        Index("ix_quote_project_id", "project_id"),
        Index("ix_quote_status", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    number = Column(String(50), nullable=False)  # "КП-0058"
    status = Column(
        Enum(QuoteStatus),
        default=QuoteStatus.DRAFT,
        nullable=False,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    project = relationship("Project", back_populates="quotes")
    versions = relationship(
        "QuoteVersion",
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteVersion.version_number",
    )
    generated_documents = relationship(
        "GeneratedDocument",
        back_populates="quote",
    )

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def latest_version(self):
        """Последняя версия КП"""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)

    @property
    def current_version(self):
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