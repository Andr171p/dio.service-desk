from typing import Protocol

from collections.abc import Sequence
from uuid import UUID

from src.shared.application.dsl import Sort
from src.shared.application.dtos import Page, Pagination, QueryDTO
from src.shared.domain.entities import Entity


class Repository[EntityT: Entity](Protocol):

    async def create(self, entity: EntityT) -> EntityT: ...

    async def read(self, uid: UUID) -> EntityT | None: ...

    async def find(
            self,
            pagination: Pagination,
            query: QueryDTO | None = None,
            sort: Sort | None = None,
    ) -> Page[EntityT]: ...

    async def update(self, entity: EntityT) -> None: ...

    async def delete(self, uid: UUID) -> None: ...

    async def exists(self, uid: UUID) -> bool: ...

    async def get_by_ids(self, ids: Sequence[UUID]) -> tuple[EntityT, ...]: ...
