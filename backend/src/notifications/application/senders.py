from typing import Any, Protocol, Self

from collections.abc import Callable

from src.notifications.domain.entities import Channel, ContactPoint, Notification
from src.notifications.domain.vo import ChannelType


class NotificationSender(Protocol):

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Self: ...

    async def send(self, notification: Notification, contact: ContactPoint) -> None: ...


type SenderType = type[NotificationSender]

_sender_registry: dict[ChannelType, SenderType] = {}

_sender_instances: dict[str, NotificationSender] = {}


def _build_instance_key(channel: Channel) -> str:
    """Формирует стабильный и детерминированный ключ на основе конфигурации канала."""

    config_hash = hash(frozenset(channel.config.items()))
    return f"{channel.id}:{config_hash}"


def register_sender(channel_type: ChannelType) -> Callable[[SenderType], SenderType]:
    """Регистрирует sender для конкретного типа канала."""

    def decorator(sender_type: SenderType) -> SenderType:
        if channel_type in _sender_registry:
            raise RuntimeError(
                f"Notification sender for '{channel_type.value}' is already registered."
            )

        _sender_registry[channel_type] = sender_type
        return sender_type

    return decorator


def get_sender(channel: Channel) -> NotificationSender:

    if (sender_type := _sender_registry.get(channel.type)) is None:
        raise LookupError(f"No notification sender registered for {channel.type.value}.")

    instance_key = _build_instance_key(channel)

    if (sender := _sender_instances.get(instance_key)) is not None:
        return sender

    sender = sender_type.from_config(channel.config)
    _sender_instances[instance_key] = sender

    return sender
