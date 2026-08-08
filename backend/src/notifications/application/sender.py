from typing import Protocol

from src.notifications.domain.entities import Notification


class NotificationSender(Protocol):

    async def send(self, notification: Notification) -> None: ...
