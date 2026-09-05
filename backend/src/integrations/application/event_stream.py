from typing import Protocol

from .dtos import EventBatch, EventQueryParamFilters


class EventStream(Protocol):

    async def read(self, filters: EventQueryParamFilters) -> EventBatch: ...

    async def ack(self): ...
