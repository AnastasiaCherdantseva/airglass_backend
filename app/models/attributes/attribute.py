import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.catalog import Unit
    from app.models.attributes import AttributeOption, CategoryAttribute, VariantAttributeValue

class AttributeDataType(str, enum.Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    OPTION = "OPTION"


class Attribute(Base, TimestampMixin):
    __tablename__ = "attributes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    data_type: Mapped[AttributeDataType] = mapped_column(
        Enum(AttributeDataType), nullable=False
    )
    unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
    )
    is_filterable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )

    # Связи
    unit: Mapped[Unit | None] = relationship(back_populates="attributes")

    options: Mapped[list[AttributeOption]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    category_attributes: Mapped[list[CategoryAttribute]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    variant_values: Mapped[list[VariantAttributeValue]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )