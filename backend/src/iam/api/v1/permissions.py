from fastapi import APIRouter, Depends, status

from src.iam.application.dtos import PermissionResponse
from src.iam.dependencies import get_permission_list
from src.shared.application.dtos import Page

router = APIRouter(prefix="/permissions", tags=["Разрешения | Permissions"])


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=PermissionResponse,
    dependencies=[],
    summary="Получить список прав",
)
async def get_permissions(
        permissions: Page[PermissionResponse] = Depends(get_permission_list),
) -> PermissionResponse:
    return permissions
