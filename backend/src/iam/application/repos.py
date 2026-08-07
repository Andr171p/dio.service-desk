from uuid import UUID

from src.iam.domain.entities import Invitation, Membership, Role, User
from src.iam.domain.vo import Email
from src.shared.domain.repos import Repository


class UserRepository(Repository[User]):

    async def get_by_email(self, email: Email) -> User | None: ...


class MembershipRepository(Repository[Membership]):

    async def get_by_user(self, user_id: UUID) -> tuple[Membership, ...]: ...

    async def get_by_user_and_organization(
            self, user_id: UUID, organization_id: UUID,
    ) -> Membership | None: ...


class RoleRepository(Repository[Role]):

    async def get_by_code(self, code: str) -> Role | None: ...


class InvitationRepository(Repository[Invitation]):

    async def get_by_token(self, token: str) -> Invitation | None: ...

    async def get_active_by_email(self, email: Email) -> tuple[Invitation, ...]: ...
