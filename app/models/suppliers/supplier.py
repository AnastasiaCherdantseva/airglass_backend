import uuid
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

# Поставщики
class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    offers = relationship(
        "SupplierVariant",
        back_populates="supplier",
        cascade="all, delete-orphan",
    )