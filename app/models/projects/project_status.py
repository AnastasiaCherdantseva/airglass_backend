import uuid
from sqlalchemy import Column, String, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProjectStatus(Base):
    __tablename__ = "project_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)
    is_final = Column(Boolean, default=False, nullable=False, server_default=text("false"))     # показывает, что проект завершён и дальше двигаться некуда.
    is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)

    # Связи
    projects = relationship("Project", back_populates="status")