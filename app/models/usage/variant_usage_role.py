from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class VariantUsageRole(Base):
    __tablename__ = "variant_usage_roles"

    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    usage_role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usage_roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    variant = relationship("ProductVariant", back_populates="variant_usage_roles")
    usage_role = relationship("UsageRole", back_populates="variant_roles")