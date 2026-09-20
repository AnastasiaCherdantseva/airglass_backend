"""
UserOrganization link model.

Many-to-many between users and organizations (ADR-USER-008).
Owner is automatically added when organization is created (BR-USERS-013).
Links are deleted physically with CASCADE (BR-USERS-012).
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import (
        Organization,
        User,
    )


class UserOrganization(Base):
    """Many-to-many link between users and organizations."""

    __tablename__ = "user_organizations"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="organization_links",
        foreign_keys=[user_id],
    )
    organization: Mapped["Organization"] = relationship(
        back_populates="user_links",
    )
