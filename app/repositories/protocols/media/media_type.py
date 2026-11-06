from typing import Protocol

from app.models.media.media_type import MediaType
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MediaTypeReadRepositoryProtocol(
    ReadRepositoryProtocol[MediaType],
    Protocol,
):
    pass


class MediaTypeWriteRepositoryProtocol(
    WriteRepositoryProtocol[MediaType],
    Protocol,
):
    pass


class MediaTypeRepositoryProtocol(
    MediaTypeReadRepositoryProtocol,
    MediaTypeWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for media types.

    Контракт репозитория типов медиа.
    """
