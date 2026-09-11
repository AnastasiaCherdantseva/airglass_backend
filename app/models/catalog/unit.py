import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Unit(Base):
    __tablename__ = "units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)  # piece, meter, kg
    name = Column(String(50), nullable=False)               # штука, метр, килограмм
    symbol = Column(String(10), nullable=False)             # шт., м, кг

    # Связи
    products = relationship("Product", back_populates="unit")
    attributes = relationship("Attribute", back_populates="unit")