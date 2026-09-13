import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.mixins import TimestampMixin
from app.models.base import Base

# правила медиа для категорий. 
# определяет, какие типы изображений разрешены для товаров определённой категории.
class CategoryMediaRule(Base, TimestampMixin):
    __tablename__ = "category_media_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_allowed = Column(Boolean, default=True, nullable=False, server_default=text("true"))
    is_required = Column(Boolean, default=False, nullable=False, server_default=text("false"))
    max_files = Column(Integer, nullable=True)

    # Связи
    category = relationship("Category", back_populates="category_media_rules")
    media_type = relationship("MediaType", back_populates="category_media_rules")