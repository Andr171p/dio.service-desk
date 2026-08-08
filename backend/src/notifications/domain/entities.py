from typing import Annotated, Any

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from typing_extensions import Doc

from src.shared.domain.entities import Entity
from src.shared.utils.time import current_datetime

from .vo import ChannelType


@dataclass(kw_only=True)
class Notification(Entity):
    """
    Пользовательское уведомление.
    Хранит факт возникновения уведомления и состояние прочтения пользователем.
    """

    user_id: UUID
    channel_id: UUID

    template_id: UUID
    template_version: int

    title: str
    message: str

    data: dict[str, Any] = field(default_factory=dict)

    sent_at: datetime | None = None
    read_at: datetime | None = None
    failed_at: datetime | None = None

    channel: ...

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_as_read(self) -> None:

        if self.is_read:
            return

        self.read_at = current_datetime()
        self.updated_at = current_datetime()


@dataclass(kw_only=True)
class UserPreference(Entity):
    """
    Настройки уведомлений для конкретного пользователя
    """

    user_id: UUID
    notification_type: str
    enabled_channels: set[ChannelType] = field(default_factory=set)
    muted_until: datetime | None = None

    def __post_init__(self) -> None:
        # 1. Добавление каналов по умолчанию
        if not self.enabled_channels:
            self.enabled_channels = {ChannelType.EMAIL, ChannelType.IN_APP}

    @property
    def is_muted(self) -> bool:
        """Активно ли временное отключение прямо сейчас"""

        return self.muted_until is not None and self.muted_until > current_datetime()

    def is_enabled_for_channel(self, channel: ChannelType) -> bool:
        """
        Проверяет, включён ли канал для данного типа уведомления
        """

        # 1. Если уведомления отключены, то канал недоступен
        if self.is_muted:
            return False

        # 2. Проверка каналов
        return channel in self.enabled_channels

    def disable_channel(self, channel: ChannelType) -> None:
        """Отключение уведомлений для конкретного канала"""

        if channel not in self.enabled_channels:
            return

        self.enabled_channels.discard(channel)
        self.updated_at = current_datetime()

    def enable_channel(self, channel: ChannelType) -> None:
        """Подключение уведомлений через конкретный канал"""

        if channel in self.enabled_channels:
            return

        self.enabled_channels.add(channel)
        self.updated_at = current_datetime()

    def mute(self, duration: timedelta) -> None:
        """
        Отключение уведомлений от всех каналов на определённый промежуток времени
        """

        if current_datetime() + duration <= current_datetime():
            raise ValueError("Mute until must be in the future")

        self.muted_until = current_datetime() + duration
        self.updated_at = current_datetime()

    def unmute(self) -> None:
        """Снимает временное отключение уведомлений"""

        if self.muted_until is not None:
            self.muted_until = None
            self.updated_at = current_datetime()


@dataclass(kw_only=True)
class Channel(Entity):
    """Канал для отправки уведомления."""

    type: ChannelType
    code: Annotated[str, Doc("Уникальное имя канала, например - 'company-email'")]
    name: str

    params: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    is_active: bool


@dataclass(kw_only=True)
class NotificationTemplate(Entity):
    """Шаблон для отображения уведомления."""

    channel_id: UUID

    name: str
    code: str

    subject: str | None = None
    body: str

    organization_id: UUID | None = None

    variables: set[str] = field(default_factory=set)
    locale: str = "ru"

    version: int
    is_default: bool = True
    is_active: bool = True
