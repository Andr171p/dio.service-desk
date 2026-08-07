from .entities import Invitation, Membership, User
from .vo import PasswordHash


def accept_for_new_user(invitation: Invitation, password_hash: str) -> tuple[User, Membership]:

    user = User(email=invitation.email, password_hash=PasswordHash(password_hash))

    membership = Membership(
        user_id=user.id,
        organization_id=invitation.organization_id,
        roles=invitation.granted_roles,
    )

    invitation.mark_as_used()

    return user, membership
