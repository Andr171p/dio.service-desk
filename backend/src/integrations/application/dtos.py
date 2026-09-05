from typing import Annotated, Any

from dataclasses import dataclass
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, NonNegativeInt


@dataclass(frozen=True, slots=True)
class EventQueryParamFilters:
    cursor: ...
    limit: Annotated[NonNegativeInt, Query(le=100, description="Лимит событий.")]
    event_types: Annotated[frozenset[str] | None, Query()] = None


class EventDTO(BaseModel):
    event_id: UUID = Field(description="Уникальный идентификатор события.")
    event_type: str = ...
    occurred_on: ...

    payload: dict[str, Any] = Field(default_factory=dict)


class EventBatch(BaseModel):
    items: list[EventDTO] = Field(default_factory=list)
    next_cursor: ...
    has_more: bool
