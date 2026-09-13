import uuid
from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Связи
    addresses = relationship(
        "CustomerAddress",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    projects = relationship("Project", back_populates="customer")