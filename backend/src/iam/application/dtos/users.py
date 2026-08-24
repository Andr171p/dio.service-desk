from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserResponse(BaseModel):
    """Данные пользователя."""

    id: UUID = Field(description="Идентификатор пользователя.")
    created_at: datetime = Field(description="Дата регистрации.")
    updated_at: datetime = Field(description="Дата последнего обновления.")

    email: EmailStr = Field(description="Email (логин пользователя).")
    username: str | None = Field(
        None, description="Никнейм пользователя.", examples=["ivan.ivanov"],
    )
    full_name: str | None = Field(
        None, description="ФИО пользователя", examples=["Иванов Иван Иванович"],
    )
    avatar_url: HttpUrl | None = Field(None, description="Ссылка на CDN с аватаркой.")
    is_active: bool = Field(description="Актива ли учётная запись.")


class CreateUserDTO(BaseModel):
    """Создание пользователя (приглашение, регистрация, ...)."""

    password: str = Field(description="Пароль пользователя")
    full_name: str | None = Field(
        None,
        description="ФИО пользователя",
        examples=["Иванов Иван Иванович"],
    )
    username: str | None = Field(
        None, description="Никнейм пользователя.", examples=["ivan.ivanov"],
    )


class UpdateUserDTO(BaseModel):
    """Запрос на изменение учётных данных."""

    username: str | None = Field(None, description="Новый никнейм.")
    full_name: str | None = Field(None, description="Новое ФИО.")
    avatar_url: HttpUrl | None = Field(None, description="Ссылка на аватарку в CDN.")


class UserQueryParamFilters(BaseModel):
    """Query param фильтры для поиска списка пользователей."""

    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
