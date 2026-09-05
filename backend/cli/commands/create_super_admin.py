from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import session_factory
from src.crm.domain.entities import Organization
from src.iam.application.permissions.registry import get_permissions
from src.iam.domain.entities import Membership, Role, User
from src.iam.domain.vo import Email, PermissionGrant, PermissionScope, SecretHash, Username
from src.iam.infra.database.repos import SqlMembershipRepository, SqlRoleRepository, SqlUserRepository
from src.iam.security import hash_password_async

_SUPER_ADMIN_ROLE_NAME = "Супер администратор"
_SUPER_ADMIN_ROLE_CODE = "super_admin"


async def _get_or_create_master_organization(session: AsyncSession) -> Organization: ...


async def _get_or_create_super_admin_role(session: AsyncSession) -> Role:
    repository = SqlRoleRepository(session)

    role = await repository.get_by_code(_SUPER_ADMIN_ROLE_CODE)
    if role is not None:
        return role

    grants = {
        PermissionGrant(permission=permission.code, scope=PermissionScope.GLOBAL)
        for permission in get_permissions()
        if PermissionScope.GLOBAL in permission.scopes
    }

    role = Role(
        name=_SUPER_ADMIN_ROLE_NAME,
        code=_SUPER_ADMIN_ROLE_CODE,
        description="Системный супер администратор платформы.",
        permissions=grants,
        is_default=True,
    )
    return await repository.create(role)


async def _get_or_create_user(
    session: AsyncSession,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    repository = SqlUserRepository(session)

    email = Email(email)
    username = Username(username) if username else None

    if (user := await repository.get_by_email(email)) is not None:
        return user

    password_hash = await hash_password_async(password)
    user = User(
        email=email,
        password_hash=SecretHash(password_hash),
        username=username,
    )
    return await repository.create(user)


async def _get_or_create_membership(
    session: AsyncSession,
    user_id: UUID,
    organization_id: UUID,
    role_id: UUID,
) -> Membership:
    repository = SqlMembershipRepository(session)

    membership = await repository.get_by_user_and_organization(user_id, organization_id)
    if membership is not None:
        return membership

    membership = Membership(
        user_id=user_id,
        organization_id=organization_id,
        roles={role_id},
    )
    return await repository.create(membership)


async def main() -> None:
    async with session_factory() as session:
        organization = await _get_or_create_master_organization(session)
        role = await _get_or_create_super_admin_role(session)
        user = await _get_or_create_user(
            session,
            email=...,
            password=...,
            username=...,
        )
        membership = await _get_or_create_membership(
            session,
            user_id=user.id,
            organization_id=organization.id,
            role_id=role.id,
        )
        await session.commit()
