from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from email.message import EmailMessage

import aiosmtplib

from .config import SmtpEmailConfig


class SmtpEmailClient:
    def __init__(self, config: SmtpEmailConfig) -> None:
        self._config = config
        self._client = aiosmtplib.SMTP()

    @asynccontextmanager
    async def _get_client(self) -> AsyncIterator[aiosmtplib.SMTP]:
        """Контекстный менеджер, который подготавливает и отдает переиспользуемый клиент."""

        if not self._client.is_connected:
            await self._client.connect(hostname=self._config.host, port=self._config.port)

            if self._config.use_tls:
                await self._client.starttls()

            if self._config.username and self._config.password:
                await self._client.login(self._config.username, self._config.password)

            try:
                yield self._client
            except aiosmtplib.SMTPException:
                self._client.close()

    def _build_message(self, recipient: str, subject: str, body: str) -> EmailMessage:

        message = EmailMessage()

        message["From"] = self._config.from_email
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        return message

    async def send(self, recipient: str, subject: str, body: str) -> None:
        message = self._build_message(recipient, subject, body)

        async with self._get_client() as client:
            await client.send_message(message)

    async def close(self) -> None:
        if self._client.is_connected:
            try:
                await self._client.quit()
            except aiosmtplib.SMTPResponseException:
                self._client.close()
