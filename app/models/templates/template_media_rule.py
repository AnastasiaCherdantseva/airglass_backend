import uuid
from sqlalchemy import Column, Boolean, Integer, ForeignKey, DateTime, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base


class TemplateMediaRule(Base):
    __tablename__ = "template_media_rules"
    __table_args__ = (
        Index("ix_template_media_rule_template_id", "template_id"),
        Index("ix_template_media_rule_media_type_id", "media_type_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    scope = Column(String(20), nullable=False, default="TEMPLATE", server_default=text("'TEMPLATE'"))  # TEMPLATE/CATEGORY/PRODUCT/VARIANT
    is_required = Column(Boolean, default=False, nullable=False, server_default=text("false"))
    max_files = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=text("now()")
    )

    # Связи
    template = relationship("Template", back_populates="media_rules")
    media_type = relationship("MediaType", back_populates="template_media_rules")