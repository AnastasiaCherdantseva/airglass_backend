import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Enum,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class DocumentType(str, enum.Enum):
    """Тип сгенерированного документа"""
    COMMERCIAL_PROPOSAL = "COMMERCIAL_PROPOSAL"  # Коммерческое предложение (PDF)


class GeneratedDocument(Base):
    """
    Сгенерированный документ (PDF).

    Хранит ссылку на файл в объектном хранилище (S3/MinIO).
    Никогда не удаляется физически — это исторический документ.

    Пример:
        Project №154
            └── Quote №58
                └── QuoteVersion v2
                    └── GeneratedDocument (PDF от 15.09.2026)
    """
    __tablename__ = "generated_documents"
    __table_args__ = (
        Index("ix_generated_document_project_id", "project_id"),
        Index("ix_generated_document_quote_id", "quote_id"),
        Index("ix_generated_document_quote_version_id", "quote_version_id"),
        Index("ix_generated_document_type", "type"),
        Index("ix_generated_document_generated_at", "generated_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ========================================
    # ССЫЛКИ (RESTRICT — защита истории)
    # ========================================
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quotes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quote_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ========================================
    # ТИП ДОКУМЕНТА
    # ========================================
    type = Column(
        Enum(DocumentType),
        default=DocumentType.COMMERCIAL_PROPOSAL,
        nullable=False,
    )

    # ========================================
    # ФАЙЛ
    # ========================================
    media_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ========================================
    # МЕТАДАННЫЕ
    # ========================================
    generated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    generated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # ========================================
    # СВЯЗИ
    # ========================================
    project = relationship("Project", back_populates="generated_documents")
    quote = relationship("Quote", back_populates="generated_documents")
    quote_version = relationship("QuoteVersion", back_populates="generated_documents")
    media_file = relationship("MediaFile", back_populates="generated_documents")

    # ========================================
    # СВОЙСТВА
    # ========================================
    @property
    def filename(self) -> str:
        """Имя файла (из media_files)"""
        return self.media_file.original_filename if self.media_file else ""

    @property
    def file_size(self) -> int:
        """Размер файла в байтах"""
        return self.media_file.file_size if self.media_file else 0

    @property
    def storage_key(self) -> str:
        """Ключ в объектном хранилище"""
        return self.media_file.storage_key if self.media_file else ""