from typing import Any

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import TEXT, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

from ..domain.vo import StatusCategory, StatusKind


class StatusOrm(Base):
    __tablename__ = "statuses"

    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"))
    workflow: Mapped["WorkflowOrm"] = relationship(back_populates="statuses")

    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    color: Mapped[str] = mapped_column(String(16))
    category: Mapped[StatusCategory] = mapped_column(Enum(StatusCategory))
    kind: Mapped[StatusKind] = mapped_column(Enum(StatusKind))

    order: Mapped[int]


class TransitionOrm(Base):
    __tablename__ = "transitions"

    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"))
    workflow: Mapped["WorkflowOrm"] = relationship(back_populates="transitions")

    name: Mapped[str] = mapped_column(String(128))

    sources: Mapped[list[UUID]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))
    destination: Mapped[UUID]

    rules: Mapped[list[Mapping[str, Any]]] = mapped_column(JSONB, default=list)

    order: Mapped[int]


class WorkflowOrm(Base):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    version: Mapped[int]
    is_default: Mapped[bool]
    is_active: Mapped[bool]
    author_id: Mapped[UUID | None] = mapped_column(nullable=True)

    initial_status_id: Mapped[UUID] = mapped_column(ForeignKey("statuses.id"), unique=False)
    statuses: Mapped[list["StatusOrm"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="StatusOrm.order",
    )
    transitions: Mapped[list["TransitionOrm"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", lazy="selectin",
    )
