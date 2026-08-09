from pydantic import BaseModel, EmailStr, Field


class SmtpEmailConfig(BaseModel):
    """Конфигурация для SMTP сервера."""

    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True

    from_email: EmailStr = Field(description="Адрес отправителя.")
