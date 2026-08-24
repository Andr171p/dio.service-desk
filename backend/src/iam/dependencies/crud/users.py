from typing import Annotated, Any

from fastapi import Depends

from src.iam.application.builders import build_user_response
from src.iam.application.dtos import CreateUserDTO, UpdateUserDTO, UserResponse
from src.iam.dependencies.base import UserRepositoryDep
from src.iam.domain.entities import User
from src.shared.application.crud import Crud
from src.shared.dependencies import TransactionDep
from src.shared.domain.helpers import apply_changes

UserCrud = Crud[
    User,
    UserResponse,
    CreateUserDTO,
    UpdateUserDTO,
    None, None, None, None,
]


async def update_handler(user: User, dto: UpdateUserDTO, options: Any | None = None) -> User:
    return apply_changes(user, **dto.model_dump())


def get_user_crud(transaction: TransactionDep, user_repository: UserRepositoryDep) -> UserCrud:
    return UserCrud(
        transaction,
        user_repository,
        build_user_response,
        update_handler=update_handler,
    )


UserCrudDep = Annotated[UserCrud, Depends(get_user_crud)]
