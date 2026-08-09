from typing import Any

from collections.abc import Mapping
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationRequest(BaseModel):
    """DTO для отправки уведомления."""

    user_id: UUID = Field(description="Идентификатор получателя.")
    organization_id: UUID | None = Field(
        None, description="Организация в которой состоит получатель.",
    )

    template_code: str = Field(description="Системный код шаблона для формирования сообщения.")
    channel_id: UUID = Field(
        description="Идентификатор канала, в который отправиться уведомление.",
    )

    context: Mapping[str, Any] = Field(description="Данные которые передаются в шаблон.")
    locale: str = Field(default="ru", description="Язык сообщения.")
