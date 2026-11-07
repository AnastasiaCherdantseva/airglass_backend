import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# справочник ролей использования товаров.
# определяет, как товар может использоваться
# в системе: как деталь обвязки, как стекло, как фурнитура и т.д.
if TYPE_CHECKING:
    from app.models import CategoryUsageRole, ProductUsageRole, VariantUsageRole


class UsageRole(Base):
    """Role of a product / variant / category in usage scenarios.

    Роль товара / варианта / категории в сценариях использования.
    """

    __tablename__ = "usage_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связи
    product_roles: Mapped[list["ProductUsageRole"]] = relationship(
        "ProductUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
    variant_roles: Mapped[list["VariantUsageRole"]] = relationship(
        "VariantUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
    category_roles: Mapped[list["CategoryUsageRole"]] = relationship(
        "CategoryUsageRole",
        back_populates="usage_role",
        cascade="all, delete-orphan",
    )
