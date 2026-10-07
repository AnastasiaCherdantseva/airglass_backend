"""
Fake-реализация UserOrganizationRepository для юнит-тестов.

In-memory: хранит пользователей, организации и связи между ними.
"""

from uuid import UUID

from app.models import Organization, User, UserOrganization


class FakeUserOrganizationRepository:
    """In-memory реализация UserOrganizationRepository."""

    def __init__(
        self,
        users: list[User] | None = None,
        organizations: list[Organization] | None = None,
        links: list[UserOrganization] | None = None,
    ) -> None:
        self.links: dict[tuple[UUID, UUID], UserOrganization] = {}
        self.organizations: dict[UUID, Organization] = {}
        self.users: dict[UUID, User] = {}

        if users:
            self.users = {user.id: user for user in users}

        if organizations:
            self.organizations = {organization.id: organization for organization in organizations}

        if links and users and organizations:
            for link in links:
                self.links[(link.user_id, link.organization_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_user_ids_by_organization_id(
        self,
        organization_id: UUID,
    ) -> list[UUID]:
        """Получить ID пользователей организации."""
        return [
            user_id
            for user_id, org_id in self.links
            if org_id == organization_id
            and user_id in self.users
            and organization_id in self.organizations
        ]

    async def get_organization_ids_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Получить ID организаций пользователя."""
        return [
            organization_id
            for linked_user_id, organization_id in self.links
            if linked_user_id == user_id
            and user_id in self.users
            and organization_id in self.organizations
        ]

    # ========================================
    # ЗАПИСЬ
    # ========================================

    def add(self, entity: UserOrganization) -> None:
        """Добавить связь в память."""
        self.links[(entity.user_id, entity.organization_id)] = entity

    async def delete(self, entity: UserOrganization) -> None:
        """Удалить связь из памяти."""
        self.links.pop(
            (entity.user_id, entity.organization_id),
            None,
        )

    async def flush(self) -> None:
        """No-op."""
        pass

    async def add_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> None:
        """Создать связь пользователя с организацией."""
        self.links[(user_id, organization_id)] = UserOrganization(
            user_id=user_id,
            organization_id=organization_id,
        )

    async def remove_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> bool:
        """Удалить связь пользователя с организацией."""
        key = (user_id, organization_id)

        if key not in self.links:
            return False

        del self.links[key]
        return True

    async def remove_by_user_id(
        self,
        user_id: UUID,
    ) -> int:
        """Удалить все связи пользователя."""
        keys = [key for key in self.links if key[0] == user_id]

        for key in keys:
            del self.links[key]

        return len(keys)

    async def remove_by_organization_id(
        self,
        organization_id: UUID,
    ) -> int:
        """Удалить все связи организации."""
        keys = [key for key in self.links if key[1] == organization_id]

        for key in keys:
            del self.links[key]

        return len(keys)
