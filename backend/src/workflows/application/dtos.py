from typing import Any

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt

from ..domain.vo import RuleKind, StatusCategory, StatusKind


class RuleResponse(BaseModel):
    """Правило/действие, которе выполняется в момент перехода."""

    type: str = Field(description="Строковый идентификатор", examples=["required_field"])
    kind: RuleKind = Field(description="Вид правила: `guard` - по перехода, `action` - после.")
    config: dict[str, Any] = Field(description="Конфигурация в формате JSON.")
    order: PositiveInt = Field(description="Порядок выполнения.")


class StatusResponse(BaseModel):
    """Статус - вершина графа Workflow."""

    id: UUID = Field(description="Идентификатор статуса.")
    created_at: datetime = Field(description="Дата создания.")
    updated_at: datetime = Field(description="Дата последнего обновления.")

    name: str = Field(description="Название статуса.", exclude=["TODO", "IN_PROGRESS"])
    description: str | None = Field(None, description="Человекочитаемое описание.")

    color: str = Field(description="HEX-код для отображения цвета в UI.", examples=["#eb4034"])
    category: StatusCategory = Field(
        description="Категория статуса: начальный, рабочий, финальный."
    )
    kind: StatusKind = Field(description="Вид статуса.")

    order: PositiveInt = Field(description="Порядковый номер.")


class TransitionResponse(BaseModel):
    """Переход между статусами Workflow (ребро графа)."""

    id: UUID = Field(description="Идентификатор перехода.")
    created_at: datetime = Field(description="Дата создания.")
    updated_at: datetime = Field(description="Дата последнего обновления.")

    sources: set[UUID] = Field(description="Статусы из которых можно совершить переход.")
    destination: UUID = Field(description="Статус в который выполняется переход.")

    guards: list[RuleResponse] = Field(
        default_factory=list, description="Правила, которые должны отработать до перехода.",
    )
    actions: list[RuleResponse] = Field(
        default_factory=list, description="Правила, которые должны отработать после перехода."
    )

# ========================================================================================
# Workflow DTOs
# ========================================================================================


class WorkflowCreate(BaseModel):
    """Создание рабочего процесса."""

    name: str = Field(description="Имя рабочего процесса", examples=["Dev - Scrum - V1"])
    description: str | None = Field(None, description="Человекочитаемое описание.")
    version: PositiveInt = Field(description="Версия Workflow", examples=[1, 2, 3])


class WorkflowResponse(BaseModel):
    """Рабочий процесс (ориентированный граф)."""

    id: UUID = Field(description="Идентификатор рабочего процесса.")
    created_at: datetime = Field(description="Дата создания.")
    updated_at: datetime = Field(description="Дата последнего обновления.")

    name: str = Field(description="Имя рабочего процесса", examples=["Dev - Scrum - V1"])
    description: str | None = Field(None, description="Человекочитаемое описание.")

    is_default: bool = Field(description="Является ли процессом по умолчанию.")
    is_active: bool = Field(description="is_active=True - процесс готов к эксплуатации.")
    version: PositiveInt = Field(description="Версия Workflow", examples=[1, 2, 3])

    initial_status_id: UUID = Field(description="Исходное состояние.")
    statuses: list[StatusResponse] = Field(
        default_factory=list, description="Все возможные статусы (вершины графа)."
    )
    transitions: list[TransitionResponse] = Field(
        default_factory=list, description="Все возможные переходы (рёбра графа)."
    )
