import uuid
import enum
from sqlalchemy import Column, String, Text, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AddressType(str, enum.Enum):
    DELIVERY = "DELIVERY"
    BILLING = "BILLING"
    OTHER = "OTHER"


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(Enum(AddressType), default=AddressType.DELIVERY, nullable=False, server_default=text("'DELIVERY'"))
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    street = Column(String(255), nullable=True)
    house = Column(String(50), nullable=True)
    apartment = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    full_address = Column(Text, nullable=True)

    # Связи
    customer = relationship("Customer", back_populates="addresses")