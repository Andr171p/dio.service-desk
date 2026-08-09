from uuid import UUID

from src.notifications.domain.entities import (
    Channel,
    ContactPoint,
    Notification,
    NotificationTemplate,
)
from src.notifications.domain.vo import ChannelType
from src.shared.application.repos import Repository


class ChannelRepository(Repository[Channel]):
    ...


class ContactRepository(Repository[ContactPoint]):

    async def find(
            self,
            user_id: UUID,
            organization_id: UUID | None = None,
            channel_id: UUID | None = None,
            channel_type: ChannelType | None = None,
    ) -> ContactPoint | None: ...


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
