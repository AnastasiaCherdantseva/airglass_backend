from typing import Protocol

from app.models.media.media_file import MediaFile
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MediaFileReadRepositoryProtocol(
    ReadRepositoryProtocol[MediaFile],
    Protocol,
):
    pass


class MediaFileWriteRepositoryProtocol(
    WriteRepositoryProtocol[MediaFile],
    Protocol,
):
    pass


class MediaFileRepositoryProtocol(
    MediaFileReadRepositoryProtocol,
    MediaFileWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for media files.

    Контракт репозитория медиафайлов.
    """
