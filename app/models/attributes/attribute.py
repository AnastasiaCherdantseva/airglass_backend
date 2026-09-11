import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class AttributeDataType(str, enum.Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    OPTION = "OPTION"


class Attribute(Base, TimestampMixin):
    __tablename__ = "attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    data_type = Column(Enum(AttributeDataType), nullable=False)
    unit_id = Column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_filterable = Column(Boolean, default=False, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)

    # Связи
    unit = relationship("Unit", back_populates="attributes")
    options = relationship(
        "AttributeOption",
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    category_attributes = relationship(
        "CategoryAttribute",
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    variant_values = relationship(
        "VariantAttributeValue",
        back_populates="attribute",
        cascade="all, delete-orphan",
    )