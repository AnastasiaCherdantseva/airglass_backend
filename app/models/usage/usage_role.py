import uuid

from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# справочник ролей использования товаров.
# определяет, как товар может использоваться
# в системе: как деталь обвязки, как стекло, как фурнитура и т.д.
class UsageRole(Base):
    __tablename__ = "usage_roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Связи
    product_roles = relationship(
        "ProductUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
    variant_roles = relationship(
        "VariantUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
    category_roles = relationship(
        "CategoryUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
