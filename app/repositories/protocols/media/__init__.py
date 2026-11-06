from app.repositories.protocols.media.category_media_rule import (
    CategoryMediaRuleReadRepositoryProtocol,
    CategoryMediaRuleRepositoryProtocol,
    CategoryMediaRuleWriteRepositoryProtocol,
)
from app.repositories.protocols.media.media_file import (
    MediaFileReadRepositoryProtocol,
    MediaFileRepositoryProtocol,
    MediaFileWriteRepositoryProtocol,
)
from app.repositories.protocols.media.media_type import (
    MediaTypeReadRepositoryProtocol,
    MediaTypeRepositoryProtocol,
    MediaTypeWriteRepositoryProtocol,
)
from app.repositories.protocols.media.product_media import (
    ProductMediaReadRepositoryProtocol,
    ProductMediaRepositoryProtocol,
    ProductMediaWriteRepositoryProtocol,
)

__all__ = [
    "CategoryMediaRuleRepositoryProtocol",
    "CategoryMediaRuleWriteRepositoryProtocol",
    "CategoryMediaRuleReadRepositoryProtocol",
    "MediaFileRepositoryProtocol",
    "MediaFileWriteRepositoryProtocol",
    "MediaFileReadRepositoryProtocol",
    "MediaTypeRepositoryProtocol",
    "MediaTypeWriteRepositoryProtocol",
    "MediaTypeReadRepositoryProtocol",
    "ProductMediaRepositoryProtocol",
    "ProductMediaWriteRepositoryProtocol",
    "ProductMediaReadRepositoryProtocol",
]
