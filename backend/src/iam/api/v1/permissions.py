from fastapi import APIRouter, status

router = APIRouter(prefix="/permissions", tags=["Разрешения | Permissions"])


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=...,
    summary="Получить список прав"
)
async def get_permissions() -> ...: ...
