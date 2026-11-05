from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security_dependencies import get_current_user
from app.dto import CurrentUser
from app.dto.system.organization import OrganizationData, OrganizationPatch
from app.repositories.deps import get_organization_repo, get_permission_condition_repo, get_user_direct_permission_repo, get_user_organization_repo, get_user_permission_repo
from app.repositories.system.organization import OrganizationRepository
from app.repositories.system.permission_condition import PermissionConditionRepository
from app.repositories.system.user_direct_permission import UserDirectPermissionRepository
from app.repositories.system.user_organization import UserOrganizationRepository
from app.repositories.system.user_permission import UserPermissionRepository
from app.schemas import OrganizationResponse
from app.schemas.system.organization import OrganizationCreateRequest, OrganizationPatchSchema
from app.use_cases import (
    create_organization,
    delete_organization,
    get_organizations,
    patch_organization,
)

router = APIRouter(prefix="/organizations", tags=["Организации"])


@router.get(
    "",
    response_model=list[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_organizations_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    user_organizations: UserOrganizationRepository = Depends(get_user_organization_repo),
) -> list[OrganizationResponse]:
    result = await get_organizations(current_user, user_organizations=user_organizations)
    return [OrganizationResponse.from_domain(o) for o in result]


@router.patch(
    "/{id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_organization_endpoint(
    id: UUID,
    body: OrganizationPatchSchema,
    current_user: CurrentUser = Depends(get_current_user),
    organizations: OrganizationRepository = Depends(get_organization_repo),
) -> OrganizationResponse:
    data = OrganizationPatch(
        id=id,
        name=body.name,
        inn=body.inn,
        address=body.address,
    )
    result = await patch_organization(current_user, data, organizations_repo=organizations)
    return OrganizationResponse.from_domain(result)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization_endpoint(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    organizations: OrganizationRepository = Depends(get_organization_repo),
) -> None:
    await delete_organization(current_user, id, organizations=organizations)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_endpoint(
    body: OrganizationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    organizations: OrganizationRepository = Depends(get_organization_repo),
    user_organizations: UserOrganizationRepository = Depends(get_user_organization_repo),
    permission_conditions: PermissionConditionRepository = Depends(get_permission_condition_repo),
    user_direct_permissions: UserDirectPermissionRepository = Depends(
        get_user_direct_permission_repo
    ),
    user_permissions: UserPermissionRepository = Depends(get_user_permission_repo),
) -> OrganizationResponse:
    data = OrganizationData(
        name=body.name,
        inn=body.inn,
        address=body.address,
    )
    result = await create_organization(
        current_user, data, organizations=organizations, user_organizations=user_organizations,
        permission_conditions=permission_conditions,
        user_direct_permissions=user_direct_permissions,
        user_permissions=user_permissions
    )
    return OrganizationResponse.from_domain(result)
