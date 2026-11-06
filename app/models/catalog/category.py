import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.attributes import CategoryAttribute
    from app.models.catalog.category_color_group import CategoryColorGroup
    from app.models.catalog.category_material_group import CategoryMaterialGroup
    from app.models.catalog.product import Product
    from app.models.media.media_file import MediaFile
    from app.models.system.permission_condition import PermissionCondition
    from app.models.templates import GalleryRuleCondition
    from app.models.usage import CategoryUsageRole


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default=text("true"),
    )
    media_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Связи
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[id],
        backref="children",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )
    category_attributes: Mapped[list["CategoryAttribute"]] = relationship(
        "CategoryAttribute",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_usage_roles: Mapped[list["CategoryUsageRole"]] = relationship(
        "CategoryUsageRole",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    media_file: Mapped[list["MediaFile"]] = relationship(
        "MediaFile",
        back_populates="categories",
        cascade="all, delete-orphan",
    )

    # category_media_rules: Mapped[list["CategoryMediaRule"]] = relationship(
    #     "CategoryMediaRule",
    #     back_populates="category",
    #     cascade="all, delete-orphan",
    # )
    category_color_groups: Mapped[list["CategoryColorGroup"]] = relationship(
        "CategoryColorGroup",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    category_material_groups: Mapped[list["CategoryMaterialGroup"]] = relationship(
        "CategoryMaterialGroup",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    gallery_rule_conditions: Mapped[list["GalleryRuleCondition"]] = relationship(
        "GalleryRuleCondition",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    conditions: Mapped[list["PermissionCondition"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
