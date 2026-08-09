import logging
from uuid import UUID

from src.notifications.domain.entities import Channel, Notification, NotificationTemplate
from src.notifications.infra.templates import render_template
from src.shared.application.repos import get_or_raise_404
from src.shared.domain.exceptions import NotFoundError

from .dtos import NotificationRequest
from .repos import ChannelRepository, ContactRepository, NotificationRepository, TemplateRepository
from .senders import get_sender

logger = logging.getLogger(__name__)


async def resolve_template(
    template_repo: TemplateRepository,
    *,
    code: str,
    channel_id: UUID,
    locale: str,
    organization_id: UUID | None,
) -> NotificationTemplate:
    """Находит шаблон организации или системный шаблон как fallback."""

    organization_template = (
        await template_repo.find(
            code=code,
            channel_id=channel_id,
            locale=locale,
            organization_id=organization_id,
        ) if organization_id is not None else None
    )

    if organization_template is not None and organization_template.is_active:
        return organization_template

    # fallback to default
    default_template = await template_repo.find(
        code=code,
        channel_id=channel_id,
        locale=locale,
        organization_id=None,
    )

    if default_template is None or not default_template.is_active:
        raise NotFoundError(
            f"Notification template '{code}' for channel '{channel_id}' was not found."
        )

    return default_template


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        template_repo: TemplateRepository,
        channel_repo: ChannelRepository,
        contact_repo: ContactRepository,
    ) -> None:
        self._template_repo = template_repo
        self._notification_repo = notification_repo
        self._channel_repo = channel_repo
        self._contact_repo = contact_repo

    async def notify(self, request: NotificationRequest) -> ...:

        channel = await get_or_raise_404(self._channel_repo.read, request.channel_id, Channel)

        template = await resolve_template(
            self._template_repo,
            code=request.template_code,
            channel_id=request.channel_id,
            locale=request.locale,
            organization_id=request.organization_id,
        )

        rendered = render_template(
            subject=template.subject, body=template.body, context=request.context,
        )

        notification = Notification(
            user_id=request.user_id,
            channel_id=channel.id,
            template_id=template.id,
            template_version=template.version,
            title=rendered.subject or "",
            message=rendered.body,
            data=dict(request.context),
        )

        await self._notification_repo.create(notification)

        sender = await get_sender(channel)

        contact = await self._contact_repo.find(
            user_id=request.user_id,
            organization_id=request.organization_id,
            channel_id=channel.id,
            channel_type=channel.type,
        )
        if contact is None:
            raise NotFoundError(
                f"No sush contacts found for "
                f"(channel={channel.type}, user={request.user_id}, "
                f"organization={request.organization_id})"
            )

        try:
            await sender.send(notification, contact)
        except Exception:
            notification.mark_as_failed()
            logger.exception("Failed to send notification - '%s'", notification.id)
        else:
            notification.mark_as_sent()

        await self._notification_repo.update(notification)
