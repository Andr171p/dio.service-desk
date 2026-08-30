from fastapi import APIRouter, Depends, status

from src.iam.application.dtos import PermissionResponse
from src.iam.application.permissions import roles
from src.iam.dependencies.permissions import permissions_list_depends, require_permissions
from src.shared.application.dtos import Page

router = APIRouter(prefix="/permissions", tags=["Разрешения | Permissions"])


@router.post(
    path="/search",
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    dependencies=[Depends(require_permissions(roles.READ))],
    summary="Получить список прав",
)
async def search_permissions(
        permissions: Page[PermissionResponse] = permissions_list_depends,
) -> PermissionResponse:
    return permissions
