import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from src.notifications.domain.entities import NotificationDelivery, NotificationTemplate
from src.shared.domain.exceptions import NotFoundError

from .repos import DeliveryRepository, TemplateRepository

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


@asynccontextmanager
async def delivery_attempt(
    delivery: NotificationDelivery, delivery_repo: DeliveryRepository,
) -> AsyncIterator[NotificationDelivery]:
    """
    Управляет жизненным циклом попытки доставки.

    Гарантирует:
    - сохранение состояния перед отправкой;
    - фиксацию успеха;
    - фиксацию ошибки.
    """

    delivery.mark_as_sending()
    await delivery_repo.update(delivery)

    try:
        yield delivery
    except Exception as exc:
        delivery.mark_as_failed(str(exc))
        logger.exception("Notification - '%s' delivery failed", delivery.notification_id)
    else:
        delivery.mark_as_sent()
    finally:
        await delivery_repo.update(delivery)
