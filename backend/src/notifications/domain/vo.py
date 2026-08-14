from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.shared.domain.vo import ValueObject


class DeliveryStatus(StrEnum):
    """Состояние доставки уведомления."""

    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class ChannelType(StrEnum):
    """Каналы куда пользователи получают уведомление."""

    EMAIL = "email"
    WEB_PUSH = "web_push"

    # Пока в планах
    TELEGRAM = "telegram"
    VK = "vk"
    MAX = "max"


@dataclass(frozen=True, slots=True)
class ChannelRef(ValueObject):
    """Ссылка на канал уведомлений."""

    type: ChannelType
    id: UUID


@dataclass(frozen=True, slots=True)
class TemplateRef(ValueObject):
    """Ссылка на шаблон сообщения."""

    id: UUID
    version: int
