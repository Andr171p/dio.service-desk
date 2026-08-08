from typing import Annotated

from fastapi import Depends

from src.core.redis import redis_client
from src.iam.application.repos import (
    InvitationRepository,
    MembershipRepository,
    RoleRepository,
    UserRepository,
)
from src.iam.infra.database.repos import (
    SqlInvitationRepository,
    SqlMembershipRepository,
    SqlRoleRepository,
    SqlUserRepository,
)
from src.shared.dependencies import DBSession
from src.shared.infra.cache import Cache, RedisCache

redis_cache = RedisCache[bool](redis_client)


def get_cache() -> Cache[bool]:
    return redis_cache


def get_user_repository(session: DBSession) -> UserRepository:
    return SqlUserRepository(session)


def get_membership_repository(session: DBSession) -> MembershipRepository:
    return SqlMembershipRepository(session)


def get_role_repository(session: DBSession) -> RoleRepository:
    return SqlRoleRepository(session)


def get_invitation_repository(session: DBSession) -> InvitationRepository:
    return SqlInvitationRepository(session)


CacheDep = Annotated[Cache[bool], Depends(get_cache)]

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
MembershipRepositoryDep = Annotated[MembershipRepository, Depends(get_membership_repository)]
RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]
InvitationRepositoryDep = Annotated[InvitationRepository, Depends(get_invitation_repository)]
