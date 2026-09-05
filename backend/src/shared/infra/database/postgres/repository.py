from typing import Any, ClassVar

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import ColumnElement, delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base
from src.shared.application.dsl import Sort
from src.shared.application.dtos import Page, Pagination, QueryDTO
from src.shared.domain.entities import Entity

from .dsl import compile_filter
from .mappers import ModelMapper
from .types import SearchFunc
from .utils import paginate


class SqlAlchemyRepository[EntityT: Entity, ModelT: Base]:
    model: type[ModelT]
    model_mapper: ModelMapper[EntityT, ModelT]
    search: SearchFunc | None = None
    filterable_fields: ClassVar[Mapping[str, ColumnElement[Any]]] = {}

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: EntityT) -> EntityT:

        model = self.model_mapper.to_model(entity)
        self._session.add(model)
        return self.model_mapper.from_model(model)

    async def read(self, uid: UUID) -> EntityT | None:
        stmt = select(self.model).where(self.model.id == uid)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else self.model_mapper.from_model(model)

    async def find(
            self,
            pagination: Pagination,
            query: QueryDTO | None = None,
            sort: Sort | None = None,
    ) -> Page[EntityT]:
        """Для расширения логики фильтрации можно переопределить в дочерних классах."""

        stmt = select(self.model)

        if query:
            stmt = stmt.where(compile_filter(query, self.filterable_fields, self.search))

        return await paginate(
            session=self._session,
            model=self.model,
            stmt=stmt,
            pagination=pagination,
            mapper=self.model_mapper.from_model,
            sort=sort,
        )

    async def update(self, entity: EntityT) -> None:
        model = self.model_mapper.to_model(entity)
        await self._session.merge(model)

    async def delete(self, uid: UUID) -> None:
        stmt = delete(self.model).where(self.model.id == uid)
        await self._session.execute(stmt)

    async def exists(self, uid: UUID) -> bool:
        stmt = select(exists()).where(self.model.id == uid)
        return await self._session.scalar(stmt)

    async def get_by_ids(self, ids: list[UUID]) -> tuple[EntityT, ...]:
        stmt = select(self.model).where(self.model.id.in_(ids))
        results = await self._session.execute(stmt)
        return [self.model_mapper.from_model(model) for model in results.scalars().all()]
