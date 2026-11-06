from typing import Protocol


class ColorVisualTypeReadRepositoryProtocol(
    Protocol,
):
    pass


class ColorVisualTypeWriteRepositoryProtocol(
    Protocol,
):
    pass


class ColorVisualTypeRepositoryProtocol(
    ColorVisualTypeReadRepositoryProtocol,
    ColorVisualTypeWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for color-visual-type links.

    Контракт репозитория связей цветов и типов визуализации.
    """

    pass
