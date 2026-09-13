import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_project_customer_id", "customer_id"),
        Index("ix_project_status_id", "status_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status_id = Column(
        UUID(as_uuid=True),
        ForeignKey("project_statuses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Связи
    customer = relationship("Customer", back_populates="projects")
    status = relationship("ProjectStatus", back_populates="projects")
    quotes = relationship(
        "Quote",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    generated_documents = relationship(
        "GeneratedDocument", back_populates="project"
    )