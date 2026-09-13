import uuid
import enum
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class TemplateType(str, enum.Enum):
    STANDARD = "STANDARD"
    BINDING = "BINDING"


class Template(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TemplateType), nullable=False, default=TemplateType.STANDARD, server_default=text("'STANDARD'"))
    is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    items = relationship(
        "TemplateItem",
        back_populates="template",
        cascade="all, delete-orphan",
    )
    media_rules = relationship(
        "TemplateMediaRule",
        back_populates="template",
        cascade="all, delete-orphan",
    )
    quote_items = relationship("QuoteItem", back_populates="template")
    quote_item_groups = relationship("QuoteItemGroup", back_populates="source_template")

    gallery = relationship(
        "TemplateGallery",
        back_populates="template",
        cascade="all, delete-orphan",
    )