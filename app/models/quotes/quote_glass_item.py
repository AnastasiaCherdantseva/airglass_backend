import uuid
from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class QuoteGlassItem(Base, TimestampMixin):
    """
    Стекло в коммерческом предложении.
    
    Отдельная сущность, потому что стёкла могут иметь
    размеры, чертежи и схемы, которых нет у обычных товаров.
    """
    __tablename__ = "quote_glass_items"
    __table_args__ = (
        Index("ix_quote_glass_item_version_id", "quote_version_id"),
        Index("ix_quote_glass_item_quote_item_id", "quote_item_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    quote_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_items.id", ondelete="CASCADE"),
        nullable=True,
    )
    name = Column(String(255), nullable=False)
    quantity = Column(Numeric(14, 4), nullable=False, default=1)

    # Размеры
    width_mm = Column(Numeric(10, 2), nullable=True)
    height_mm = Column(Numeric(10, 2), nullable=True)
    thickness_mm = Column(Numeric(10, 2), nullable=True)

    # Характеристики
    glass_type = Column(String(100), nullable=True)  # прозрачное, матовое, бронза
    area_m2 = Column(Numeric(10, 4), nullable=True)

    comment = Column(Text, nullable=True)

    # Связи
    quote_version = relationship("QuoteVersion", back_populates="glass_items")
    quote_item = relationship("QuoteItem")
    media = relationship(
        "QuoteGlassMedia",
        back_populates="quote_glass_item",
        cascade="all, delete-orphan",
    )

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def calculated_area_m2(self) -> float | None:
        """Площадь в м² (автоматический расчёт)"""
        if self.width_mm and self.height_mm:
            area = (float(self.width_mm) * float(self.height_mm)) / 1_000_000
            return round(area, 4)
        return None