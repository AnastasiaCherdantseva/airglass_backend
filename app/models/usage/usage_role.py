import uuid
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# справочник ролей использования товаров. 
# определяет, как товар может использоваться 
# в системе: как деталь обвязки, как стекло, как фурнитура и т.д.
class UsageRole(Base):
    __tablename__ = "usage_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)

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