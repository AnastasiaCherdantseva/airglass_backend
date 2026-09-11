from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductUsageRole(Base):
    __tablename__ = "product_usage_roles"

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )
    usage_role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usage_roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    product = relationship("Product", back_populates="product_usage_roles")
    usage_role = relationship("UsageRole", back_populates="product_roles")