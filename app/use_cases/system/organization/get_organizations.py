from app.dto import CurrentUser, OrganizationOutPut
from app.repositories.protocols.system.user_organization import (
    UserOrganizationReadRepositoryProtocol,
)


async def get_organizations(
    actor: CurrentUser,
    *,
    user_organizations: UserOrganizationReadRepositoryProtocol,
) -> list[OrganizationOutPut]:
    """
    Получить организации текущего пользователя.

    На MVP пользователь видит только организации, с которыми
    у него есть связь.
    """
    organizations = await user_organizations.get_organizations_by_user_id(actor.id)
    return organizations
