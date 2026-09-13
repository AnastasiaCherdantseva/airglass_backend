import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class GalleryRule(Base, TimestampMixin):
    """
    Глобальное правило для галереи шаблонов.
    
    Настраивается пользователем ОДИН РАЗ.
    Применяется ко ВСЕМ шаблонам.
    
    Примеры:
    - "Только стекло"
    - "Стекло + Фурнитура"
    - "Стекло + Фурнитура + Ручки"
    """
    __tablename__ = "gallery_rules"
    __table_args__ = (
        Index("ix_gallery_rule_code", "code"),
        Index("ix_gallery_rule_is_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # ✅ Приоритет: чем больше — тем важнее
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

    # ========================================
    # СВЯЗИ
    # ========================================
    conditions = relationship(
        "GalleryRuleCondition",
        back_populates="rule",
        cascade="all, delete-orphan",
    )
    template_galleries = relationship("TemplateGallery", back_populates="rule")