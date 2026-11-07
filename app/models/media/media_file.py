import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.catalog.category import Category
    from app.models.documents.generated_document import GeneratedDocument
    from app.models.media.product_media import ProductMedia
    from app.models.media.user_media import UserMedia
    from app.models.templates.template_gallery import TemplateGallery


class MediaFile(Base, TimestampMixin):
    """Registry of all media files (images, drawings, PDFs).

    Реестр всех медиафайлов (изображений, чертежей, PDF).
    """

    __tablename__ = "media_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    # относительный путь к файлу
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    product_media: Mapped[list["ProductMedia"]] = relationship(
        "ProductMedia",
        back_populates="media_file",
    )
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="media_file",
        uselist=False,
    )
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship(
        "GeneratedDocument",
        back_populates="media_file",
    )
    user_media: Mapped[list["UserMedia"]] = relationship(
        "UserMedia",
        back_populates="media_file",
    )
    template_gallery: Mapped[list["TemplateGallery"]] = relationship(
        "TemplateGallery",
        back_populates="media_file",
    )
