from dataclasses import dataclass
from enum import StrEnum

from src.shared.domain.vo import ValueObject


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
    code: str
