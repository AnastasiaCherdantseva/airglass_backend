import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuoteGlassMedia(Base):
    """
    Изображения стекла в КП (чертежи, схемы, фото).
    """
    __tablename__ = "quote_glass_media"
    __table_args__ = (
        Index("ix_quote_glass_media_glass_item_id", "quote_glass_item_id"),
        Index("ix_quote_glass_media_media_file_id", "media_file_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_glass_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_glass_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False,
    )
    type = Column(String(50), nullable=False)  # GLASS_DRAWING / GLASS_SCHEME / PHOTO
    sort_order = Column(Integer, default=0, nullable=False)

    # Связи
    quote_glass_item = relationship("QuoteGlassItem", back_populates="media")
    media_file = relationship("MediaFile", back_populates="quote_glass_media")