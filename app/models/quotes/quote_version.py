import uuid
from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class QuoteVersion(Base, TimestampMixin):
    """
    Версия коммерческого предложения.
    
    Это конкретная версия с зафиксированными ценами и данными заказчика.
    Клиент получил v1 — она неизменна.
    Ты создал v2 — это новая версия.
    """
    __tablename__ = "quote_versions"
    __table_args__ = (
        Index("ix_quote_version_quote_id", "quote_id"),
        Index("ix_quote_version_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number = Column(Integer, nullable=False, default=1)

    # Глобальные скидки/наценки на всё КП
    global_discount_percent = Column(Numeric(5, 2), default=0, nullable=False)
    global_markup_percent = Column(Numeric(5, 2), default=0, nullable=False)

    # Snapshot данных заказчика (не меняются после сохранения)
    customer_name_snapshot = Column(Text, nullable=True)
    customer_phone_snapshot = Column(Text, nullable=True)
    customer_email_snapshot = Column(Text, nullable=True)
    delivery_address_snapshot = Column(Text, nullable=True)

    notes = Column(Text, nullable=True)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    quote = relationship("Quote", back_populates="versions")
    groups = relationship(
        "QuoteItemGroup",
        back_populates="quote_version",
        cascade="all, delete-orphan",
        order_by="QuoteItemGroup.sort_order",
    )
    items = relationship(
        "QuoteItem",
        back_populates="quote_version",
        cascade="all, delete-orphan",
        order_by="QuoteItem.sort_order",
    )
    glass_items = relationship(
        "QuoteGlassItem",
        back_populates="quote_version",
        cascade="all, delete-orphan",
    )
    generated_documents = relationship(
        "GeneratedDocument",
        back_populates="quote_version",
    )

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def total_amount(self) -> float:
        """Итоговая сумма по всем позициям"""
        total = sum(float(item.final_total) for item in self.items)
        return round(total, 2)

    @property
    def total_with_global_discount(self) -> float:
        """Сумма с учётом глобальной скидки/наценки"""
        total = self.total_amount
        if self.global_markup_percent:
            total += total * float(self.global_markup_percent) / 100
        if self.global_discount_percent:
            total -= total * float(self.global_discount_percent) / 100
        return round(total, 2)

    @property
    def items_count(self) -> int:
        """Количество позиций"""
        return len(self.items)

    @property
    def groups_count(self) -> int:
        """Количество групп (обвязок/шаблонов)"""
        return len(self.groups)