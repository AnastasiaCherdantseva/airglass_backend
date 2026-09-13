import uuid
from sqlalchemy import Column, ForeignKey, Integer, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class GalleryRuleCondition(Base):
    """
    Условие глобального правила галереи.
    
    Пример:
    Rule "Стекло + Фурнитура":
    ├── condition 1: category = "Стекло"
    └── condition 2: category = "Фурнитура"
    """
    __tablename__ = "gallery_rule_conditions"
    __table_args__ = (
        Index("ix_gallery_rule_condition_rule_id", "rule_id"),
        Index("ix_gallery_rule_condition_category_id", "category_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gallery_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)

    # ========================================
    # СВЯЗИ
    # ========================================
    rule = relationship("GalleryRule", back_populates="conditions")
    category = relationship("Category", back_populates="gallery_rule_conditions")