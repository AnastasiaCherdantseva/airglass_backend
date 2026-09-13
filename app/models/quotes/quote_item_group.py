import uuid
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuoteItemGroupType(str, enum.Enum):
    """Тип группы позиций"""
    TEMPLATE = "TEMPLATE"    # группа из шаблона
    BINDING = "BINDING"      # группа обвязки
    MANUAL = "MANUAL"        # ручная группа


class QuoteItemGroup(Base):
    """
    Группа позиций в КП.
    
    Пример:
        ОГРАЖДЕНИЕ №1
        ├── Петля × 2
        ├── Ручка × 1
        └── Стекло × 1
        
        🔗 ОБВЯЗКА
        ├── Профиль × 3
        ├── Коннектор × 2
        └── Уплотнитель × 4
    """
    __tablename__ = "quote_item_groups"
    __table_args__ = (
        Index("ix_quote_item_group_version_id", "quote_version_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    quote_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(
        Enum(QuoteItemGroupType),
        default=QuoteItemGroupType.MANUAL,
        nullable=False,
        server_default=text("'MANUAL'")
    )
    source_template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String(255), nullable=False)  # "ОГРАЖДЕНИЕ №1"
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)

    # Связи
    quote_version = relationship("QuoteVersion", back_populates="groups")
    source_template = relationship("Template", back_populates="quote_item_groups")
    items = relationship(
        "QuoteItem",
        back_populates="group",
        order_by="QuoteItem.sort_order",
    )

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def total_amount(self) -> float:
        """Сумма по группе"""
        total = sum(float(item.final_total) for item in self.items)
        return round(total, 2)

    @property
    def is_binding(self) -> bool:
        """Является ли группа обвязкой"""
        return self.type == QuoteItemGroupType.BINDING