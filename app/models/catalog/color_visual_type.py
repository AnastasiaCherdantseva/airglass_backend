import uuid
from sqlalchemy import (
    Column, Integer, ForeignKey, Index, UniqueConstraint, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ColorVisualType(Base):
    """
    Связь цвета с типом визуализации.
    
    Пример:
    Цвет "Прозрачное стекло":
    ├── TRANSPARENT
    ├── GLOSS
    └── ...

    Цвет "Матовое стекло":
    ├── MATTE
    └── ...

    Цвет "Дуб":
    ├── WOOD_GRAIN
    ├── MATTE
    └── ...
    """
    __tablename__ = "color_visual_types"
    __table_args__ = (
        UniqueConstraint(
            "color_id", "visual_type_id",
            name="uq_color_visual_type",
        ),
        Index("ix_color_visual_type_color_id", "color_id"),
        Index("ix_color_visual_type_visual_type_id", "visual_type_id"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    color_id = Column(
        UUID(as_uuid=True),
        ForeignKey("colors.id", ondelete="CASCADE"),
        nullable=False,
    )
    visual_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("visual_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Связи
    color = relationship("Color", back_populates="color_visual_types")
    visual_type = relationship("VisualType", back_populates="color_visual_types")