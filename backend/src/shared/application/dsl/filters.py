from decimal import Decimal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from .operators import ComparisonOperator, LogicOperator

type ScalarValue = UUID | AwareDatetime | Decimal | str | int | float | bool | None
type RichJsonValue = (
    ScalarValue
    | set[RichJsonValue]
    | list[RichJsonValue]
    | tuple[RichJsonValue, ...]
)


class Condition(BaseModel):
    """Условие фильтрации по одному полю."""

    field: str = Field(description="Имя поля")
    op: ComparisonOperator = Field(description="Оператор сравнения.")
    value: RichJsonValue | None = Field(default=None, description="Значение для сравнения.")


class Group(BaseModel):
    """Группа условий, объединённых логическим оператором."""

    op: LogicOperator = Field(description="Логический оператор.")
    filters: tuple["Filter", ...] = Field(description="Условия группы.")


class Negation(BaseModel):
    """Отрицание сложной группы (логика Де Моргана)."""

    filter_: "Filter" = Field(alias="filter", description="Условие которое нужно отрицать.")


class Search(BaseModel):
    """Полнотекстовый поиск."""

    query: str = Field(description="Поисковый запрос.")


type Filter = Condition | Group | Negation | Search

__all__ = ["Condition", "Filter", "Group", "Negation", "Search"]
