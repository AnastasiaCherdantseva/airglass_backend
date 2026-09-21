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
    __table_args__ = (
        # BR-ORG-003.ADR-ORG-002.
        UniqueConstraint("inn", name="uq_organizations_inn"),
        # BR-ORG-004.ADR-ORG-003.
        UniqueConstraint("owner_id", "name", name="uq_organizations_owner_name"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    # BR-ORG-001. BR-ORG-002.BR-ORG-008.ADR-ORG-005.
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # BR-ORG-002.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # BR-ORG-002
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped["User"] = relationship(
        back_populates="organizations",
        foreign_keys=[owner_id],
    )
    # BR-ORG-006.ADR-ORG-007.
    user_links: Mapped[list["UserOrganization"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
