from src.notifications.domain.entities import ContactPoint, Notification
from src.notifications.domain.vo import ChannelType
from src.notifications.infra.email.smtp import SmtpEmailClient, SmtpEmailConfig

from .base import BaseNotificationSender, register_sender


@register_sender(ChannelType.EMAIL, config=SmtpEmailClient)
class EmailNotificationSender(BaseNotificationSender[SmtpEmailConfig, SmtpEmailClient]):

    @staticmethod
    def _create_client(config: SmtpEmailConfig) -> SmtpEmailClient:
        return SmtpEmailClient(config)

    async def send(self, notification: Notification, contact: ContactPoint) -> None:
        client = await self._get_client()

        await client.send(
            recipient=contact.value, subject=notification.title, body=notification.message,
        )

    async def close(self) -> None:
        await self._client.close()
