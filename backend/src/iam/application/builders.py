from uuid import UUID

from src.crm.application.dtos import OrganizationRef
from src.crm.domain.entities import Organization
from src.iam.domain.entities import Membership

from .dtos import LoginResponse, MembershipResponse


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
