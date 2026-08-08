from uuid import UUID

from src.notifications.domain.entities import Channel, Notification, NotificationTemplate
from src.shared.application.repos import Repository


class ChannelRepository(Repository[Channel]):
    ...


class NotificationRepository(Repository[Notification]):
    ...


class TemplateRepository(Repository[NotificationTemplate]):

    async def find(
            self,
            *,
            code: str,
            channel_id: UUID,
            locale: str,
            organization_id: UUID | None,
    ) -> NotificationTemplate | None: ...
