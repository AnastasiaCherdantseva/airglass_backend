import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# правила медиа для категорий. 
# определяет, какие типы изображений разрешены для товаров определённой категории.
class CategoryMediaRule(Base):
    __tablename__ = "category_media_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    is_allowed = Column(Boolean, default=True, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    max_files = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Связи
    category = relationship("Category", back_populates="category_media_rules")
    media_type = relationship("MediaType", back_populates="category_media_rules")