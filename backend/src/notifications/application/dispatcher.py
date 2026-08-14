from src.notifications.domain.entities import Channel, Notification, NotificationDelivery
from src.notifications.domain.vo import DeliveryStatus
from src.shared.application.repos import get_or_raise_404
from src.shared.application.uow import UnitOfWork

from .repos import ChannelRepository, ContactRepository, DeliveryRepository, NotificationRepository
from .senders import get_sender
from .services import delivery_attempt


class NotificationDispatcher:
    def __init__(
            self,
            uow: UnitOfWork,
            contact_repo: ContactRepository,
            channel_repo: ChannelRepository,
            delivery_repo: DeliveryRepository,
            notification_repo: NotificationRepository,
    ) -> None:
        self._uow = uow
        self._contact_repo = contact_repo
        self._channel_repo = channel_repo
        self._delivery_repo = delivery_repo
        self._notification_repo = notification_repo

    async def dispatch(self, notification: Notification):

        channel = await get_or_raise_404(self._channel_repo.read, notification.channel.id, Channel)
        contact_point = await self._contact_repo.get_primary(...)

        delivery = NotificationDelivery(
            notification_id=notification.id,
            channel_id=channel.id,
            contact_point_id=contact_point.id,
            status=DeliveryStatus.PENDING,
        )
        await self._delivery_repo.create(delivery)
        await self._uow.commit()

        sender = get_sender(channel)

        async with delivery_attempt(delivery, self._delivery_repo):
            await sender.send(notification, contact_point)

        await self._uow.commit()
