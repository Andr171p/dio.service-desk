from uuid import UUID

from pydantic import HttpUrl

from src.crm.application.dtos import OrganizationRef
from src.crm.domain.entities import Organization
from src.iam.domain.entities import Membership, User

from .dtos import LoginResponse, MembershipResponse, UserResponse


def build_login_response(
        authentication_token: str,
        memberships: tuple[Membership, ...],
        organizations: tuple[Organization, ...],
) -> LoginResponse:
    organizations_map: dict[UUID, Organization] = {
        organization.id: organization for organization in organizations
    }

    return LoginResponse(
        authentication_token=authentication_token,
        memberships=[
            MembershipResponse(
                id=membership.id,
                joined_at=membership.created_at,
                organization=OrganizationRef(
                    id=organization.id,
                    name=organization.name,
                    kind=organization.kind,
                ),
            )
            for membership in memberships
            if (organization := organizations_map.get(membership.organization_id)) is not None
        ]
    )


def build_user_response(user: User) -> UserResponse:
    username = user.username.value if user.username is not None else None
    full_name = user.full_name.value if user.full_name is not None else None

    avatar_url = HttpUrl(user.avatar_url) if user.avatar_url is not None else None

    return UserResponse(
        id=user.id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        email=user.email.value,
        username=username,
        full_name=full_name,
        avatar_url=avatar_url,
        is_active=user.is_active,
    )
