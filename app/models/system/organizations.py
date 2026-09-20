from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import (
        User,
        UserOrganization,
    )


class Organization(
    Base,
    TimestampMixin,
):
    """Organization owned by the user who created it."""

    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("inn", name="uq_organizations_inn"),
        UniqueConstraint("owner_id", "name", name="uq_organizations_owner_name"),
    )

    owner: Mapped["User"] = relationship(
        back_populates="organizations",
        foreign_keys=[owner_id],
    )
    user_links: Mapped[list["UserOrganization"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
