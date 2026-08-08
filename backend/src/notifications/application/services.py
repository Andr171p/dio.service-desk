from uuid import UUID

from src.notifications.domain.entities import NotificationTemplate
from src.shared.domain.exceptions import NotFoundError

from .repos import ChannelRepository, NotificationRepository, TemplateRepository


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
    ) -> None:
        self._template_repo = template_repo
        self._notification_repo = notification_repo
        self._channel_repo = channel_repo

    async def send(self): ...
