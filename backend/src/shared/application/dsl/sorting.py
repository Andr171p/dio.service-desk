from typing import Literal

from dataclasses import dataclass

type SortDirection = Literal["asc", "desc"]


@dataclass(frozen=True, slots=True)
class Sort:
    field: str
    direction: SortDirection = "asc"


def parse_sort_from_query_param(param: str | None) -> Sort:
    """Парсит query-параметр сортировки."""

    cleaned = param.strip()
    if not cleaned:
        raise ValueError("Sort query param cannot be empty.")

    if cleaned.startswith("-"):
        field = cleaned[1:]
        direction: SortDirection = "desc"

    elif ":" in cleaned:
        field, raw_direction = cleaned.split(":", maxsplit=1)
        direction = raw_direction.lower()

    else:
        field = cleaned
        direction = "asc"

    if not field:
        raise ValueError("Sort field cannot be empty.")

    if direction not in ("asc", "desc"):
        raise ValueError(f"Invalid sort direction: {direction!r}. " "Expected 'asc' or 'desc'.", )

    return Sort(field=field, direction=direction)


__all__ = ["Sort", "SortDirection", "parse_sort_from_query_param"]
