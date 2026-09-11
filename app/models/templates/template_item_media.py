import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class TemplateItemMedia(Base):
    __tablename__ = "template_item_media"
    __table_args__ = (
        Index("ix_template_item_media_item_id", "template_item_id"),
        Index("ix_template_item_media_media_file_id", "media_file_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_items.id", ondelete="CASCADE"),
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
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Связи
    template_item = relationship("TemplateItem", back_populates="media")
    media_file = relationship("MediaFile", back_populates="template_item_media")
    media_type = relationship("MediaType", back_populates="template_item_media")