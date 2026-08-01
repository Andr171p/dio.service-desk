from typing import Any

from datetime import datetime
from uuid import UUID

from pydantic import UUID5, BaseModel, Field, PositiveInt

from ..domain.vo import RuleKind, StatusCategory, StatusKind


class RuleCreate(BaseModel):
    """Создание конфигурации правила."""

    type: str = Field(description="Строковый идентификатор", examples=["required_field"])
    kind: RuleKind = Field(description="Вид правила: `guard` - по перехода, `action` - после.")
    config: dict[str, Any] = Field(description="Конфигурация в формате JSON.")
    order: PositiveInt = Field(description="Порядок выполнения.")


class RuleUpdate(BaseModel):
    """Обновление конфигурации правила."""

    config: dict[str, Any] | None = Field(None, description="Конфигурация в формате JSON.")
    order: PositiveInt | None = Field(None, description="Порядок выполнения.")


class RuleResponse(BaseModel):
    """Правило/действие, которе выполняется в момент перехода."""

    id: UUID5 = Field(
        description="Детерминированный идентификатор, вычисляется на основе атрибутов.",
    )
    type: str = Field(description="Строковый идентификатор", examples=["required_field"])
    kind: RuleKind = Field(description="Вид правила: `guard` - по перехода, `action` - после.")
    config: dict[str, Any] = Field(description="Конфигурация в формате JSON.")
    order: PositiveInt = Field(description="Порядок выполнения.")


# ========================================================================================
# Status DTOs
# ========================================================================================


class StatusCreate(BaseModel):
    """Добавить новый статус."""

    name: str = Field(description="Название статуса.", exclude=["TODO", "IN_PROGRESS"])
    description: str | None = Field(None, description="Человекочитаемое описание.")

    color: str = Field(description="HEX-код для отображения цвета в UI.", examples=["#eb4034"])
    category: StatusCategory = Field(
        description="Категория статуса: начальный, рабочий, финальный."
    )
    kind: StatusKind = Field(description="Вид статуса.")

    order: PositiveInt = Field(description="Порядковый номер.")


class StatusUpdate(BaseModel):
    """Обновить статус."""

    name: str | None = Field(
        None, description="Название статуса.", exclude=["TODO", "IN_PROGRESS"],
    )
    description: str | None = Field(None, description="Человекочитаемое описание.")

    color: str | None = Field(
        None, description="HEX-код для отображения цвета в UI.", examples=["#eb4034"],
    )
    category: StatusCategory | None = Field(
        None, description="Категория статуса: начальный, рабочий, финальный.",
    )
    kind: StatusKind | None = Field(None, description="Вид статуса.")

    order: PositiveInt | None = Field(None, description="Порядковый номер.")


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


# ========================================================================================
# Transition DTOs
# ========================================================================================


class TransitionCreate(BaseModel):
    """Создание перехода Workflow."""

    name: str = Field(description="Человекочитаемое название перехода.")

    sources: set[UUID] = Field(description="Статусы из которых можно совершить переход.")
    destination: UUID = Field(description="Статус в который выполняется переход.")

    rules: list[RuleCreate] = Field(
        default_factory=list, description="Правила которые должны выполниться при переходе."
    )


class TransitionUpdate(BaseModel):
    """Обновление перехода между статусами."""

    name: str | None = Field(None, description="Человекочитаемое название перехода.")

    sources: set[UUID] = Field(
        default_factory=set, description="Статусы из которых можно совершить переход.",
    )
    destination: UUID | None = Field(None, description="Статус в который выполняется переход.")


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


class WorkflowUpdate(BaseModel):
    """Редактирование справочной информации."""

    name: str | None = None
    description: str | None = None


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
    author_id: UUID | None = Field(None, description="Автор рабочего процесса.")

    initial_status_id: UUID | None = Field(None, description="Исходное состояние.")
    statuses: list[StatusResponse] = Field(
        default_factory=list, description="Все возможные статусы (вершины графа)."
    )
    transitions: list[TransitionResponse] = Field(
        default_factory=list, description="Все возможные переходы (рёбра графа)."
    )
