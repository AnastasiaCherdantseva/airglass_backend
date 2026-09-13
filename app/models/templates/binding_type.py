import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class BindingType(Base, TimestampMixin):
    """
    Справочник типов обвязки.
    
    Используется в шаблонах обвязки (Template.type = BINDING).
    """
    __tablename__ = "binding_types"
    __table_args__ = (
        Index("ix_binding_type_code", "code"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        server_default=text("true"),
    )

    # Связи
    templates = relationship("Template", back_populates="binding_type")