import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models import (
        TemplateItem,
        TemplateMediaRule,
        QuoteItem,
        QuoteItemGroup,
        TemplateGallery,
        BindingType,
    )


class TemplateType(str, enum.Enum):
    STANDARD = "STANDARD"
    BINDING = "BINDING"


class Template(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[TemplateType] = mapped_column(
        Enum(TemplateType),
        default=TemplateType.STANDARD,
        server_default=text("'STANDARD'"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )
    binding_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("binding_types.id", ondelete="RESTRICT"),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    # Связи
    items: Mapped[list["TemplateItem"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )
    media_rules: Mapped[list["TemplateMediaRule"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )
    quote_items: Mapped[list["QuoteItem"]] = relationship(back_populates="template")
    quote_item_groups: Mapped[list["QuoteItemGroup"]] = relationship(
        back_populates="source_template",
    )

    gallery: Mapped[list["TemplateGallery"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )
    binding_type: Mapped["BindingType | None"] = relationship(
        back_populates="templates",
    )

    @property
    def has_gallery(self) -> bool:
        """Есть ли у шаблона галерея (по правилам)."""
        return len(self.media_rules) > 0