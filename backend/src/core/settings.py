from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEZONE = ZoneInfo("Asia/Yekaterinburg")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

INSTALLED_MODULES: tuple[str, ...] = (  # Добавь сюда модуль который готов к использованию
    "iam",
)

load_dotenv(ENV_FILE)


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    port: int = 8000
    version: str = Field(description="Актуальная версия приложения.", examples=["12.5.1"])

    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


class SuperAdminConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SUPER_ADMIN_")

    email: str = "admin@admin.com"
    password: str = "admin"
    username: str = "admin"
    full_name: str = Field(
        default="Админов Админ Админович",
        description="ФИО для нормального отображения в системе."
    )


class Settings(BaseSettings):
    secret_key: str = "<SECRET_KEY>"
    frontend_url: str = "http://localhost:3000"


app_config = AppConfig()  # type: ignore
super_admin_config = SuperAdminConfig()
