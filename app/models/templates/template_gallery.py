import uuid
from sqlalchemy import Column, Boolean, Integer, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class TemplateGallery(Base, TimestampMixin):
    """
    Галерея изображений шаблона.
    
    Привязана к ГЛОБАЛЬНОМУ правилу.
    
    Пример:
    Шаблон "Душевая 1200":
    ├── Rule "Только стекло":
    │   └── image1.jpg (primary)
    │
    └── Rule "Стекло + Фурнитура":
        └── image2.jpg (primary)
    """
    __tablename__ = "template_gallery"
    __table_args__ = (
        Index("ix_template_gallery_template_id", "template_id"),
        Index("ix_template_gallery_rule_id", "rule_id"),
        Index("ix_template_gallery_media_file_id", "media_file_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gallery_rules.id", ondelete="RESTRICT"),
        nullable=False,
    )
    media_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False,
    )
    media_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # ✅ Для порядка и приоритета
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)
    is_primary = Column(Boolean, default=False, nullable=False, server_default=text("false"))

    # ========================================
    # СВЯЗИ
    # ========================================
    template = relationship("Template", back_populates="gallery")
    rule = relationship("GalleryRule", back_populates="template_galleries")
    media_file = relationship("MediaFile", back_populates="template_gallery")
    media_type = relationship("MediaType", back_populates="template_gallery")