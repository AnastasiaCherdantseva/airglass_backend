import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.customers import Customer


class AddressType(str, enum.Enum):
    DELIVERY = "DELIVERY"
    BILLING = "BILLING"
    OTHER = "OTHER"


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
    )
    type: Mapped[AddressType] = mapped_column(
        Enum(AddressType),
        default=AddressType.DELIVERY,
        server_default=text("'DELIVERY'"),
    )
    country: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    street: Mapped[str | None] = mapped_column(String(255))
    house: Mapped[str | None] = mapped_column(String(50))
    apartment: Mapped[str | None] = mapped_column(String(50))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    full_address: Mapped[str | None] = mapped_column(Text)

    # Связи
    customer: Mapped["Customer"] = relationship(back_populates="addresses")