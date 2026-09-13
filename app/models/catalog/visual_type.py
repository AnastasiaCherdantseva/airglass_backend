import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class VisualType(Base, TimestampMixin):
    """
    Справочник типов визуализации цвета.
    
    Примеры:
    - TRANSPARENT (полупрозрачность)
    - GLOSS (блик)
    - MATTE (матовость)
    - WOOD_GRAIN (текстура дерева)
    - SPECKLES (крапинки)
    - METALLIC (металлик)
    """
    __tablename__ = "visual_types"
    __table_args__ = (
        Index("ix_visual_type_code", "code"),
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
    color_visual_types = relationship(
        "ColorVisualType",
        back_populates="visual_type",
        cascade="all, delete-orphan",
    )