import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import QuoteVersion, Template, QuoteItem


class QuoteItemGroupType(str, enum.Enum):
    """Тип группы позиций"""
    TEMPLATE = "TEMPLATE"    # группа из шаблона
    BINDING = "BINDING"      # группа обвязки
    MANUAL = "MANUAL"        # ручная группа


class QuoteItemGroup(Base):
    """
    Группа позиций в КП.
    """
    __tablename__ = "quote_item_groups"
    __table_args__ = (
        Index("ix_quote_item_group_version_id", "quote_version_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    quote_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="CASCADE"),
    )
    type: Mapped[QuoteItemGroupType] = mapped_column(
        Enum(QuoteItemGroupType),
        default=QuoteItemGroupType.MANUAL,
        server_default=text("'MANUAL'"),
    )
    source_template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="SET NULL"),
    )
    name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
    )

    # Связи
    quote_version: Mapped["QuoteVersion"] = relationship(back_populates="groups")
    source_template: Mapped["Template | None"] = relationship(
        back_populates="quote_item_groups",
    )
    items: Mapped[list["QuoteItem"]] = relationship(
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