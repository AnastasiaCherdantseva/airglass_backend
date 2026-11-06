from typing import Protocol

from app.models.media.media_type import MediaType
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MediaTypeRepositoryProtocol(
    ReadRepositoryProtocol[MediaType],
    WriteRepositoryProtocol[MediaType],
    Protocol,
):
    """Repository contract for media types.

    Контракт репозитория типов медиа.
    """
