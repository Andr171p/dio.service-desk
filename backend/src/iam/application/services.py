from datetime import timedelta
from uuid import UUID

from src.core.settings import settings
from src.crm.application.repos import OrganizationRepository
from src.iam.domain.entities import Membership, Role, User
from src.iam.domain.exceptions import UnauthorizedError
from src.iam.domain.vo import Email
from src.iam.security import (
    create_access_token,
    create_authentication_token,
    create_refresh_token,
    decode_token,
    verify_password_async,
)
from src.shared.utils.time import get_expiration_timestamp

from .builders import build_login_response
from .dtos import LoginResponse, TokenRequest, TokensResponse, UserCredentials
from .repos import MembershipRepository, RoleRepository, UserRepository


def _verify_authentication_token(token: str) -> UUID:
    """Поверяет токен аутентификации, возвращает идентификатор пользователя."""

    payload = decode_token(token)

    if payload.get("typ") != "authentication":
        raise UnauthorizedError("Invalid token type.")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Missing required 'sub' claim in token payload.")

    return user_id


def _create_tokens_for_user(
        user: User, membership: Membership, roles: set[Role],
) -> TokensResponse:
    """Выпуск пары токенов для пользователя."""

    permissions = {permission for role in roles for permission in role.permissions}

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        membership_id=membership.id,
        organization_id=membership.organization_id,
        roles={role.code for role in roles},
        permissions=permissions,
    )
    refresh_token = create_refresh_token(user_id=user.id, membership_id=membership.id)

    access_token_expires_at = get_expiration_timestamp(
        expires_in=timedelta(minutes=settings.jwt.access_token_expires_in_minutes),
    )

    return TokensResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=access_token_expires_at,
    )


class AuthService:
    def __init__(
            self,
            user_repo: UserRepository,
            membership_repo: MembershipRepository,
            role_repo: RoleRepository,
            organization_repo: OrganizationRepository,
    ) -> None:
        self._user_repo = user_repo
        self._membership_repo = membership_repo
        self._role_repo = role_repo
        self._organization_repo = organization_repo

    async def login(self, credentials: UserCredentials) -> LoginResponse:
        """Поверяет учётную запись и выдаёт токен для аутентификации."""

        email = Email(credentials.email)

        if (user := await self._user_repo.get_by_email(email)) is None:
            raise UnauthorizedError(f"User account - '{email}' not found.")

        if (
            not await verify_password_async(
                credentials.password, user.password_hash.get_hashed_value(),
            )
            or not user.is_active
        ):
            raise UnauthorizedError("Invalid credentials or user is not active.")

        memberships = await self._membership_repo.get_by_user(user.id)

        organization_ids = [membership.organization_id for membership in memberships]
        organizations = await self._organization_repo.get_by_ids(organization_ids)

        authentication_token = create_authentication_token(user.id)

        return build_login_response(
            authentication_token=authentication_token,
            memberships=memberships,
            organizations=organizations,
        )

    async def authenticate(self, request: TokenRequest) -> TokensResponse:
        """Получение пары токенов в выбранной организации."""

        user_id = _verify_authentication_token(request.authentication_token)

        if (user := await self._user_repo.read(user_id)) is None:
            raise UnauthorizedError(f"User - '{user_id}' not found.")

        if (membership := await self._membership_repo.read(request.membership_id)) is None:
            raise UnauthorizedError(f"Membership - '{request.membership_id}' not found.")

        if membership.user_id != user_id:
            raise UnauthorizedError("")

        roles = await self._role_repo.get_by_ids(list(membership.roles))

        return _create_tokens_for_user(user=user, membership=membership, roles=roles)

    async def refresh_tokens(self) -> ...: ...

    async def logout(self) -> ...: ...


class RegistrationService:
    def __init__(self) -> None:
        ...

    async def register(self) -> ...: ...
