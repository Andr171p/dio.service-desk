from typing import Any

from collections.abc import Callable, Mapping

from sqlalchemy import ColumnElement, Select, UnaryExpression, and_, asc, desc, not_, or_

from src.core.database import Base
from src.shared.application.dsl import (
    Condition,
    Filter,
    Group,
    Negation,
    Search,
    Sort,
    SortDirection,
)

from .types import SearchFunc

type SortFunc = Callable[[ColumnElement[Any]], UnaryExpression[Any]]


def compile_filter(
    filter_: Filter,
    fields: Mapping[str, ColumnElement[Any]],
    search: SearchFunc | None = None,
) -> ColumnElement[bool]:
    """
    Компилирует абстрактный DSL-фильтр в выражение SQLAlchemy.

    Функция является точкой входа для компиляции фильтров. Она рекурсивно
    разбирает структуру фильтра (условие, логическая группа или отрицание)
    и преобразует её в соответствующий объект `ColumnElement` из SQLAlchemy.
    """

    if isinstance(filter_, Condition):
        return _compile_condition(filter_, fields)

    if isinstance(filter_, Search) and search is None:
        raise ValueError("Full-text search is not supported.")

    if isinstance(filter_, Group):
        return _compile_group(filter_, fields, search)

    if isinstance(filter_, Negation):
        return not_(compile_filter(filter_.filter_, fields, search))

    raise ValueError(f"Unsupported filter type: {type(filter_)}")


def _compile_condition(  # noqa: C901, PLR0911
    condition: Condition,
    fields: Mapping[str, ColumnElement[Any]],
) -> ColumnElement[bool]:
    """Компилирует одиночное атомарное условие (Condition) в выражение SQLAlchemy.

    Функция маппит строковые операторы DSL (например, `"$eq"`, `"$in"`, `"$ilike"`)
    в соответствующие операторы сравнения или методы колонок SQLAlchemy.
    """

    if (column := fields.get(condition.field)) is None:
        raise ValueError(f"Unknown filter field: '{condition.field}'.")

    match condition.op:
        case "$eq":
            return column == condition.value

        case "$ne":
            return column != condition.value

        case "$gt":
            return column > condition.value

        case "$gte":
            return column >= condition.value

        case "$lt":
            return column < condition.value

        case "$lte":
            return column <= condition.value

        case "$in":
            _ensure_list_value(condition)
            return column.in_(condition.value)

        case "$nin":
            _ensure_list_value(condition)
            return column.not_in(condition.value)

        case "$like":
            return column.like(_ensure_str_value(condition))

        case "$ilike":
            return column.ilike(_ensure_str_value(condition))

        case "$isNull":
            return column.is_(None)

        case "$isNotNull":
            return column.is_not(None)

    raise ValueError(f"Unsupported filter operator: '{condition.op}'")


def _compile_group(
    group: Group,
    fields: Mapping[str, ColumnElement[Any]],
    search: SearchFunc | None,
) -> ColumnElement[bool]:
    """Компилирует группу фильтров (Group) объединяя их логическим оператором AND или OR.

    Функция рекурсивно вызывает `compile_filter` для каждого дочернего фильтра
    в группе, а затем оборачивает их в SQLAlchemy-функции `and_()` или `or_()`.
    """

    filters = tuple(compile_filter(filter_, fields, search) for filter_ in group.filters)

    if not filters:
        raise ValueError("Filter group cannot be empty.")

    match group.op:
        case "$and":
            return and_(*filters)

        case "$or":
            return or_(*filters)

    raise ValueError(f"Unsupported logic operator: '{group.op}'")


def _ensure_list_value(condition: Condition) -> list[Any]:
    """
    Проверяет, что значение в условии является списком.
    Используется для валидации значений операторов `"$in"` и `"$nin"`.
    """
    if not isinstance(condition.value, list):
        raise ValueError(f"Operator '{condition.op}' expects a list value.")

    return condition.value


def _ensure_str_value(condition: Condition) -> str:
    """
    Проверяет, что значение в условии является строкой.
    Используется для валидации значений операторов `"$like"` и `"$ilike"`.
    """
    if not isinstance(condition.value, str):
        raise ValueError(f"Operator '{condition.op}' expects a string value.")

    return condition.value


def _get_sort_func(direction: SortDirection) -> SortFunc:
    return asc if direction.lower() == "asc" else desc


def apply_sorting[ModelT: Base](
    stmt: Select[tuple[ModelT]],
    model: type[ModelT],
    sort: Sort | None = None,
) -> Select[tuple[ModelT]]:
    """Динамически накладывает order_by на основе параметров из фильтра."""

    default_stmt = stmt.order_by(model.created_at)

    if sort is None:
        return default_stmt

    sort_func = _get_sort_func(sort.direction)

    try:
        if (column := getattr(model, sort.field, None)) is not None:
            return stmt.order_by(sort_func(column))

    except (AttributeError, ValueError):
        raise ValueError(f"Invalid sort query param - '{sort}'") from None

    return default_stmt


__all__ = ["apply_sorting", "compile_filter"]
