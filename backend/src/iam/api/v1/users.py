from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.iam.application.dtos import UpdateUserDTO, UserResponse
from src.iam.dependencies import CurrentIdentity, get_current_identity
from src.iam.dependencies.crud import UserCrudDep, get_current_user, get_users_list
from src.shared.application.dtos import Page

router = APIRouter(prefix="/users", tags=["Пользователи | Users"])


@router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
    summary="Получить текущего пользователя",
)
async def get_me(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return user


@router.patch(
    path="/me",
    status_code=status.HTTP_200_OK,
    summary="Обновить данные текущего пользователя."
)
async def update_me(
        identity: CurrentIdentity,
        dto: UpdateUserDTO,
        crud: UserCrudDep,
) -> UserResponse:
    return crud.update(identity.id, dto)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    dependencies=[get_current_identity],
    summary="Получить список пользователей",
)
async def get_users(users: Page[UserResponse] = Depends(get_users_list)) -> Page[UserResponse]:
    return users


@router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_identity)],
    summary="Получить конкретного пользователя",
)
async def get_user(user_id: UUID, crud: UserCrudDep) -> UserResponse:
    return await crud.read(user_id)
