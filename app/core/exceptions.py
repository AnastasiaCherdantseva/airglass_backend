"""
Доменные исключения — не знают ни про HTTP, ни про SQLAlchemy.
"""


class DomainError(Exception):
    """Базовое доменное исключение."""
    pass


class NotFoundError(DomainError):
    """Сущность не найдена."""
    pass


class ConflictError(DomainError):
    """Конфликт: дубликат, нарушение уникальности."""
    pass


class ValidationError(DomainError):
    """Ошибка бизнес-валидации."""
    pass


class PermissionDeniedError(DomainError):
    """Недостаточно прав."""
    pass