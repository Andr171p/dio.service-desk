from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.shared.infra.database.types import (
    datetime_null,
    datetime_tz,
    str_null,
    str_unique,
    text_null,
)


class UserOrm(Base):
    __tablename__ = "users"

    email: Mapped[str_unique]
    username: Mapped[str_null]
    full_name: Mapped[str_null]
    avatar_url: Mapped[str_null]
    password_hash: Mapped[str_unique]
    is_active: Mapped[bool]

    memberships: Mapped[list["MembershipOrm"]] = relationship(back_populates="user")

    __table_args__ = (
        Index("ix_users_is_active", "is_active"),
    )


class MembershipOrm(Base):
    __tablename__ = "memberships"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=False)
    organization_id: Mapped[UUID]
    roles: Mapped[list[UUID]] = mapped_column(JSONB)
    expires_at: Mapped[datetime_null]
    is_active: Mapped[bool]

    user: Mapped["UserOrm"] = relationship(back_populates="memberships")


class RoleOrm(Base):
    __tablename__ = "roles"

    name: Mapped[str]
    code: Mapped[str_unique]
    description: Mapped[text_null]

    permissions: Mapped[list[str]] = mapped_column(JSONB)
    is_default: Mapped[bool]


class InvitationOrm(Base):
    __tablename__ = "invitations"

    email: Mapped[str]
    token: Mapped[str]
    invited_by: Mapped[UUID]

    granted_roles: Mapped[list[UUID]] = mapped_column(JSONB)
    organization_id: Mapped[UUID]
    expires_at: Mapped[datetime_tz]

    used_at: Mapped[datetime_null]
    is_used: Mapped[bool]
