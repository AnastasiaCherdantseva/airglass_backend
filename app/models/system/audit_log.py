import uuid
from datetime import datetime,timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_entity", "entity_type", "entity_id"),
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)  # CREATE / UPDATE / DELETE
    old_data = Column(JSONB, nullable=True)
    new_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))

    # Связи
    user = relationship("User", back_populates="audit_logs")