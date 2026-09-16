import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.catalog.unit import Unit
    from app.models.attributes.attribute_option import AttributeOption
    from app.models.attributes.category_attribute import CategoryAttribute
    from app.models.attributes.variant_attribute_value import VariantAttributeValue


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
    data_type: Mapped[AttributeDataType] = mapped_column(Enum(AttributeDataType))
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

    # Связи — В КАВЫЧКАХ, потому что импорт под TYPE_CHECKING
    unit: Mapped["Unit | None"] = relationship(back_populates="attributes")

    options: Mapped[list["AttributeOption"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    category_attributes: Mapped[list["CategoryAttribute"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )
    variant_values: Mapped[list["VariantAttributeValue"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )