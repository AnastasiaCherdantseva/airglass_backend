from typing import Protocol

from app.models.media.media_file import MediaFile
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MediaFileRepositoryProtocol(
    ReadRepositoryProtocol[MediaFile],
    WriteRepositoryProtocol[MediaFile],
    Protocol,
):
    """Repository contract for media files.

    Контракт репозитория медиафайлов.
    """
