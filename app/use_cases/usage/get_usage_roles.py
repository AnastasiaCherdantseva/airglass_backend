from app.dto.usage.usage_role import UsageRoleOutput
from app.repositories.protocols.usage.usage_role import UsageRoleReadRepositoryProtocol


async def get_usage_roles(
    *,
    usage_roles: UsageRoleReadRepositoryProtocol,
) -> list[UsageRoleOutput]:
    return await usage_roles.get_all()
