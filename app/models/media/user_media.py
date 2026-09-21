import uuid

from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class UserMedia(Base, TimestampMixin):
    """
    Медиа пользователя.

    Одна запись на (user, media_type).

    Примеры:
    - USER_AVATAR — аватарка
    - COMPANY_LOGO — лого компании
    - CONTRACT_TEMPLATE — шаблон договора
    - INN — ИНН
    - OGRN — ОГРН
    """

    __tablename__ = "user_media"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "media_type_id",
            name="uq_user_media_user_type",
        ),
        Index("ix_user_media_user_id", "user_id"),
        Index("ix_user_media_media_file_id", "media_file_id"),
        Index("ix_user_media_media_type_id", "media_type_id"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_files.id", ondelete="RESTRICT"),
        nullable=False,
    )
    media_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media_types.id", ondelete="RESTRICT"),
        nullable=False,
    )

    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )

    # ========================================
    # СВЯЗИ
    # ========================================
    user = relationship("User", back_populates="user_media")
    media_file = relationship("MediaFile", back_populates="user_media")
    media_type = relationship("MediaType", back_populates="user_media")
