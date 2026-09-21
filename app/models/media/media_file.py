import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

# реестр всех медиафайлов (изображений, чертежей, PDF) в системе.
# Сами файлы физически хранятся в объектном хранилище , а в этой таблице — метаданные и ссылки на них.


class MediaFile(Base, TimestampMixin):
    __tablename__ = "media_files"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    storage_key = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    product_media = relationship("ProductMedia", back_populates="media_file")
    generated_documents = relationship("GeneratedDocument", back_populates="media_file")
    user_media = relationship("UserMedia", back_populates="media_file")
    template_gallery = relationship("TemplateGallery", back_populates="media_file")
