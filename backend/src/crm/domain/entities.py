from typing import Annotated, Any

from dataclasses import dataclass, field
from uuid import UUID

from typing_extensions import Doc

from src.iam.domain.vo import Email, FullName
from src.shared.domain.entities import AggregateRoot, Entity
from src.shared.domain.exceptions import InvariantViolationError
from src.shared.utils.time import current_datetime

from .vo import Address, BusinessProfile, PhoneNumber


@dataclass(kw_only=True)
class ContactPerson(Entity):
    """
    Контактное лицо организации.
    Используется для связи с контрагентами, отправки уведомлений
    и сопоставления с учетными записями пользователей в системе.
    """

    full_name: FullName

    phone: PhoneNumber | None = None
    email: Email | None = None
    additional_info: dict[str, Any] = field(default_factory=dict)

    user_id: Annotated[UUID | None, Doc("Идентификатор реального пользователя.")] = None

    is_primary: Annotated[bool, Doc("Является ли контакт основным.")] = False
    is_active: bool = True


def _validate_organization_contacts(contacts: dict[UUID, ContactPerson]) -> None:
    """"""

    primary_contacts = sum(
        contact.is_primary and contact.is_active for contact in contacts.values()
    )

    if primary_contacts > 1:
        raise InvariantViolationError("Organization cannot have multiple primary contacts.")

    if any(contact.is_primary and not contact.is_active for contact in contacts.values()):
        raise InvariantViolationError("Inactive contact cannot be primary.")


@dataclass(kw_only=True)
class Organization(AggregateRoot):
    """"""

    name: str
    email: Email | None = None
    phone: PhoneNumber | None = None

    business_profile: BusinessProfile
    addresses: set[Address] = field(default_factory=set)
    contacts: dict[UUID, ContactPerson] = field(default_factory=dict)

    parent_id: UUID | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        _validate_organization_contacts(self.contacts)

    def add_contact(self, contact: ContactPerson) -> None:
        if contact.id in self.contacts:
            raise InvariantViolationError(f"Contact {contact.id} already belongs to organization.")

        if contact.is_primary:
            ...

        self.contacts[contact.id] = contact
        self.updated_at = current_datetime()

    def remove_contact(self, contact_id: UUID) -> None: ...
