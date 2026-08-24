from dataclasses import dataclass, field
from enum import IntEnum, auto
from uuid import UUID

from src.iam.domain.vo import Email


class IdentityType(IntEnum):
    """Тип субъекта авторизации."""

    USER = auto()
    SERVICE_ACCOUNT = auto()
    AI_AGENT = auto()


@dataclass(frozen=True, slots=True)
class Identity:
    """Субъект авторизации - аутентифицированная сущность выполняющая запрос."""

    id: UUID
    type: IdentityType

    email: Email | None = None
    organization_id: UUID | None = None
    membership_id: UUID | None = None

    roles: frozenset[str] = field(default_factory=frozenset)
    permissions: frozenset[str] = field(default_factory=frozenset)
