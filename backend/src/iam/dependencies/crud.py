from typing import Annotated

from uuid import UUID

from fastapi import Depends

from src.iam.application.builders import build_user_response
from src.iam.application.crud import role as role_crud
from src.iam.application.dtos import UserQueryParamFilters, UserResponse
from src.iam.domain.entities import User
from src.shared.application.dtos import Page
from src.shared.application.repos import get_or_raise_404
from src.shared.dependencies import PaginationDep

from .base import UserRepositoryDep
from .identity import CurrentIdentity


async def get_current_user(
        identity: CurrentIdentity, user_repo: UserRepositoryDep,
) -> UserResponse:
    """Зависимость для получения текущего пользователя (делает запрос в БД)."""

    user = await get_or_raise_404(user_repo.read, identity.id, User)
    return build_user_response(user)


async def get_user_or_404(user_id: UUID, user_repo: UserRepositoryDep) -> UserResponse:
    """Зависимость для получения пользователя по его ID."""

    user = await get_or_raise_404(user_repo.read, user_id, User)
    return build_user_response(user)


async def get_user_list(
        pagination: PaginationDep,
        filters: Annotated[UserQueryParamFilters, Depends()],
        user_repo: UserRepositoryDep,
) -> Page[UserResponse]:
    page = await user_repo.find(pagination, filters=filters)
    return page.to_response(build_user_response)


def get_role_crud() -> ...:
    ...
