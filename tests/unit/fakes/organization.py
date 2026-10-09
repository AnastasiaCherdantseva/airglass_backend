from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from app.dto import OrganizationData, OrganizationOutPut, OrganizationPatch
from app.models import Organization


class FakeOrganizationRepository:
    """In-memory реализация OrganizationRepository."""

    def __init__(
        self,
        organizations: list[Organization] | None = None,
    ) -> None:
        self.organizations: dict[UUID, Organization] = {}

        if organizations:
            self.organizations = {organization.id: organization for organization in organizations}

    @staticmethod
    def _unique_violation(constraint_name: str) -> IntegrityError:
        """Собрать IntegrityError с поведением asyncpg."""
        orig = SimpleNamespace(constraint_name=constraint_name)
        return IntegrityError(
            "duplicate key value violates unique constraint",
            None,
            orig,
        )

    @staticmethod
    def _to_output(
        organization: Organization,
    ) -> OrganizationOutPut:
        """Преобразовать модель организации в DTO."""
        return OrganizationOutPut(
            id=organization.id,
            owner_id=organization.owner_id,
            name=organization.name,
            inn=organization.inn,
            address=organization.address,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )

    # ========================================
    # ЧТЕНИЕ
    # ========================================
    async def get_by_ids(self, ids: list[UUID]) -> list[OrganizationOutPut]:
        """Get organizations by their IDs.

        Получить организации по их идентификаторам.
        """
        return [
            self._to_output(self.organizations[organization_id])
            for organization_id in ids
            if organization_id in self.organizations
        ]

    async def get_by_id(
        self,
        organization_id: UUID,
    ) -> Organization | None:
        """Получить организацию по ID."""
        return self.organizations.get(organization_id)

    async def get_by_owner_id(
        self,
        user_id: UUID,
    ) -> list[OrganizationOutPut]:
        """Получить организации пользователя как владельца."""
        return [
            self._to_output(organization)
            for organization in self.organizations.values()
            if organization.owner_id == user_id
        ]

    async def get_by_inn(self, inn: str) -> OrganizationOutPut | None:
        """Get an organization by INN.

        Получить организацию по ИНН.
        """
        organization = next(
            (item for item in self.organizations.values() if item.inn == inn),
            None,
        )
        return self._to_output(organization) if organization is not None else None

    async def get_by_owner_id_and_name(
        self,
        user_id: UUID,
        name: str,
    ) -> OrganizationOutPut | None:
        """Get an organization by owner and name.

        Получить организацию по владельцу и названию.
        """
        organization = next(
            (
                item
                for item in self.organizations.values()
                if item.owner_id == user_id and item.name == name
            ),
            None,
        )
        return self._to_output(organization) if organization is not None else None

    # ========================================
    # ЗАПИСЬ
    # ========================================

    async def create_for_user(
        self,
        user_id: UUID,
        data: OrganizationData,
    ) -> OrganizationOutPut:
        """Создать организацию с указанным пользователем как владельцем."""
        if any(organization.inn == data.inn for organization in self.organizations.values()):
            raise self._unique_violation("uq_organizations_inn")

        if any(
            organization.owner_id == user_id and organization.name == data.name
            for organization in self.organizations.values()
        ):
            raise self._unique_violation("uq_organizations_owner_name")

        organization = Organization(
            id=uuid4(),
            owner_id=user_id,
            name=data.name,
            inn=data.inn,
            address=data.address,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.organizations[organization.id] = organization

        return self._to_output(organization)

    async def patch(
        self,
        data: OrganizationPatch,
    ) -> OrganizationOutPut | None:
        """Обновить организацию."""
        organization = self.organizations.get(data.id)
        if organization is None:
            return None

        if data.name is not None and data.name != organization.name:
            if any(
                o.owner_id == organization.owner_id and o.name == data.name
                for o in self.organizations.values()
                if o.id != data.id
            ):
                raise self._unique_violation("uq_organizations_owner_name")
            organization.name = data.name
        if data.inn is not None and data.inn != organization.inn:
            if any(o.inn == data.inn for o in self.organizations.values() if o.id != data.id):
                raise self._unique_violation("uq_organizations_inn")
            organization.inn = data.inn
        if data.address is not None:
            organization.address = data.address
        organization.updated_at = datetime.now(UTC)
        return self._to_output(organization)

    async def delete_by_owner_ids(
        self,
        owner_ids: list[UUID],
    ) -> int:
        """Удалить организации указанных владельцев."""
        if not owner_ids:
            return 0

        organization_ids = [
            organization_id
            for organization_id, organization in self.organizations.items()
            if organization.owner_id in owner_ids
        ]

        for organization_id in organization_ids:
            del self.organizations[organization_id]

        return len(organization_ids)

    async def delete_by_id(self, organization_id: UUID) -> bool:
        """Удалить организацию по ID."""
        if organization_id not in self.organizations:
            return False

        del self.organizations[organization_id]
        return True

    def add(self, entity: Organization) -> None:
        """Добавить организацию в память."""
        self.organizations[entity.id] = entity

    async def delete(self, entity: Organization) -> None:
        """Удалить организацию из памяти."""
        self.organizations.pop(entity.id, None)

    async def flush(self) -> None:
        """No-op."""
        pass
