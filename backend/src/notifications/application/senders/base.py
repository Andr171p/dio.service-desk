from typing import Any, Protocol

from abc import ABC, abstractmethod
from collections.abc import Callable
from uuid import UUID

from pydantic import BaseModel

from src.notifications.domain.entities import Channel, ContactPoint, Notification
from src.notifications.domain.vo import ChannelType


class NotificationSender(Protocol):

    async def send(self, notification: Notification, contact: ContactPoint) -> None: ...


class BaseNotificationSender[ConfigT, ClientT](ABC):
    def __init__(self, config: ConfigT) -> None:
        self._config = config
        self._client: ClientT | None = None

    def accepts_config(self, config: ConfigT) -> bool:
        """Проверяет, соответствует ли конфигурация текущему sender."""

        return self._config == config

    async def _get_client(self) -> ClientT:
        if self._client is not None:
            return self._client

        self._client = self._create_client(self._config)
        return self._client

    @staticmethod
    @abstractmethod
    async def _create_client(config: ConfigT) -> ClientT:
        """Создаёт transport client для переданной конфигурации."""

    @abstractmethod
    async def send(self, notification: Notification, contact: ContactPoint) -> None: ...

    @abstractmethod
    async def close(self) -> None:
        """Освобождает ресурсы transport client."""


type AnySender = BaseNotificationSender[Any, Any]
type SenderDefinition = tuple[type[BaseModel], type[AnySender]]


_sender_types: dict[ChannelType, SenderDefinition] = {}
_sender_instances: dict[UUID, AnySender] = {}


def register_sender[ConfigT: BaseModel](
    channel_type: ChannelType,
    *,
    config: type[ConfigT],
) -> Callable[[type[AnySender]], type[AnySender]]:
    """Регистрирует sender и Pydantic-схему его конфигурации."""

    def decorator(sender_type: type[AnySender]) -> type[AnySender]:
        if channel_type in _sender_types:
            raise RuntimeError(
                f"Notification sender for '{channel_type.value}' is already registered."
            )

        _sender_types[channel_type] = (config, sender_type)
        return sender_type

    return decorator


async def get_sender(channel: Channel) -> NotificationSender:
    """Возвращает переиспользуемый sender для конкретного канала."""

    try:
        config_cls, sender_cls = _sender_types[channel.type]
    except KeyError:
        raise LookupError(
            f"No notification sender registered for channel '{channel.type.value}'."
        ) from None

    config = config_cls.model_validate(channel.params)

    current_sender = _sender_instances.get(channel.id)

    if current_sender is not None and current_sender.accepts_config(config):
        return current_sender

    if current_sender is not None:
        await current_sender.close()

    sender = sender_cls(config)
    _sender_instances[channel.id] = sender

    return sender
