import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import session_factory
from src.crm.domain.entities import Organization
from src.iam.application.permissions.registry import get_permissions
from src.iam.domain.entities import Membership, Role, User
from src.iam.domain.vo import Email, PermissionGrant, PermissionScope, SecretHash, Username
from src.iam.infra.database.repos import SqlMembershipRepository, SqlRoleRepository, SqlUserRepository
from src.iam.security import hash_password_async

logger = logging.getLogger(__name__)

_SUPER_ADMIN_ROLE_NAME = "Супер администратор"
_SUPER_ADMIN_ROLE_CODE = "super_admin"


async def _get_or_create_master_organization(session: AsyncSession) -> Organization: ...


async def _get_or_create_super_admin_role(session: AsyncSession) -> Role:
    repository = SqlRoleRepository(session)

    logger.info("Checking super admin role: code=%s", _SUPER_ADMIN_ROLE_CODE)

    role = await repository.get_by_code(_SUPER_ADMIN_ROLE_CODE)
    if role is not None:
        logger.info("Super admin role already exists")
        return role

    grants = {
        PermissionGrant(permission=permission.code, scope=PermissionScope.GLOBAL)
        for permission in get_permissions()
        if PermissionScope.GLOBAL in permission.scopes
    }

    logger.info("Creating super admin role with %d global permission grants", len(grants))

    role = Role(
        name=_SUPER_ADMIN_ROLE_NAME,
        code=_SUPER_ADMIN_ROLE_CODE,
        description="Системный супер администратор платформы.",
        permissions=grants,
        is_default=True,
    )

    created = await repository.create(role)
    logger.info(
        "Super admin role created: code=%s, grants=%d, createdAt=%s",
        _SUPER_ADMIN_ROLE_CODE,
        len(grants),
        created.created_at,
    )
    return created


async def _get_or_create_user(
    session: AsyncSession,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    repository = SqlUserRepository(session)

    email = Email(email)
    username = Username(username) if username else None

    logger.info("Checking super admin user: email=%s", email.value)

    if (user := await repository.get_by_email(email)) is not None:
        logger.info("Super admin user already exists: id=%s, email=%s", user.id, email.value)
        return user

    logger.info("Creating super admin user: email=%s", email.value, )

    password_hash = await hash_password_async(password)
    user = User(
        email=email,
        password_hash=SecretHash(password_hash),
        username=username,
    )
    created = await repository.create(user)
    logger.info(
        "Super admin user created: id=%s, email=%s, createdAt=%s",
        user.id,
        email.value,
        created.created_at,
    )
    return created


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
        _ = await _get_or_create_membership(
            session,
            user_id=user.id,
            organization_id=organization.id,
            role_id=role.id,
        )
        await session.commit()
