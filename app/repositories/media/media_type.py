from app.models.media.media_type import MediaType
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.media.media_type import (
    MediaTypeReadRepositoryProtocol,
    MediaTypeWriteRepositoryProtocol,
)


class MediaTypeRepository(
    BaseIdRepository[MediaType], MediaTypeReadRepositoryProtocol, MediaTypeWriteRepositoryProtocol
):
    """Repository for media types.

    Репозиторий типов медиа.
    """

    model = MediaType
