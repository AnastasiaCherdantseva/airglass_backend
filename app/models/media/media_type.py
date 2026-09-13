import uuid
from sqlalchemy import Column, String, Text, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# типы файлов
class MediaType(Base):
    __tablename__ = "media_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False, server_default=text("false"))

    # Связи
    category_media_rules = relationship(
        "CategoryMediaRule",
        back_populates="media_type",
        cascade="all, delete-orphan",
    )
    template_media_rules = relationship(
        "TemplateMediaRule",
        back_populates="media_type",
        cascade="all, delete-orphan",
    )
    user_media = relationship("UserMedia", back_populates="media_type")
    template_gallery = relationship("TemplateGallery", back_populates="media_type")