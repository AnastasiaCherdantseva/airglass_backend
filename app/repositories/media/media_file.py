from app.models.media.media_file import MediaFile
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.media.media_file import (
    MediaFileReadRepositoryProtocol,
    MediaFileWriteRepositoryProtocol,
)


class MediaFileRepository(
    BaseIdRepository[MediaFile], MediaFileReadRepositoryProtocol, MediaFileWriteRepositoryProtocol
):
    """Repository for media files.

    Репозиторий медиафайлов.
    """

    model = MediaFile
