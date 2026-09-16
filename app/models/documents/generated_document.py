import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Enum,
    DateTime,
    Index,
    text,
    Column
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Project, Quote,QuoteVersion, MediaFile


class DocumentType(str, enum.Enum):
    """Тип сгенерированного документа"""
    COMMERCIAL_PROPOSAL = "COMMERCIAL_PROPOSAL"


class GeneratedDocument(Base):
    """
    Сгенерированный документ (PDF).

    Хранит ссылку на файл в объектном хранилище (S3/MinIO).
    Никогда не удаляется физически — это исторический документ.
    """
    __tablename__ = "generated_documents"
    __table_args__ = (
        Index("ix_generated_document_project_id", "project_id"),
        Index("ix_generated_document_quote_id", "quote_id"),
        Index("ix_generated_document_quote_version_id", "quote_version_id"),
        Index("ix_generated_document_type", "type"),
        Index("ix_generated_document_generated_at", "generated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # ========================================
    # ССЫЛКИ (RESTRICT — защита истории)
    # ========================================
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
    )
    quote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotes.id", ondelete="RESTRICT"),
    )
    quote_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="RESTRICT"),
    )

    # ========================================
    # ТИП ДОКУМЕНТА
    # ========================================
    type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
        default=DocumentType.COMMERCIAL_PROPOSAL,
        server_default=text("'COMMERCIAL_PROPOSAL'"),
    )

    # ========================================
    # ФАЙЛ
    # ========================================
    media_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
    )

    # ========================================
    # МЕТАДАННЫЕ
    # ========================================
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )

    # ========================================
    # СВЯЗИ
    # ========================================
    project: Mapped["Project"] = relationship(back_populates="generated_documents")
    quote: Mapped["Quote"] = relationship(back_populates="generated_documents")
    quote_version: Mapped["QuoteVersion"] = relationship(back_populates="generated_documents")
    media_file: Mapped["MediaFile"] = relationship(back_populates="generated_documents")

    # ========================================
    # СВОЙСТВА
    # ========================================
    @property
    def filename(self) -> Column[str] | str:
        """Имя файла (из media_files)"""
        return self.media_file.original_filename if self.media_file else ""

    @property
    def file_size(self) -> Column[int] |int:
        """Размер файла в байтах"""
        return self.media_file.file_size if self.media_file else 0

    @property
    def storage_key(self) -> Column[str] |str:
        """Ключ в объектном хранилище"""
        return self.media_file.storage_key if self.media_file else ""