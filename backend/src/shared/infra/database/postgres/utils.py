from collections.abc import Callable

from sqlalchemy import Select, func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property

from src.core.database import Base
from src.shared.application.dsl import Sort
from src.shared.application.dtos import Page, Pagination

from .dsl import apply_sorting


def get_filterable_fields[ModelT: Base](model: type[ModelT]) -> tuple[str, ...]:
    """Автоматически собирает все имена колонок и гибридных свойств модели."""

    mapper = inspect(model)
    fields = set()

    for attr in mapper.attrs:
        if hasattr(attr, "columns"):
            fields.add(attr.key)

    for key, expr in mapper.all_orm_descriptors.items():
        if isinstance(expr, hybrid_property):
            fields.add(key)

    return tuple(fields)


async def paginate[ModelT: Base, ItemT](
        session: AsyncSession,
        model: type[ModelT],
        stmt: Select[tuple[ModelT]],
        pagination: Pagination,
        *,
        mapper: Callable[[ModelT], ItemT] | None = None,
        sort: Sort | None = None,
) -> Page[ItemT]:
    count_stmt = select(func.count()).select_from(stmt.subquery())

    if not (total := await session.scalar(count_stmt)):
        return Page.create([], total, pagination.page, pagination.size)

    stmt = stmt.offset(pagination.offset).limit(pagination.size)
    stmt = apply_sorting(stmt, model, sort)

    results = await session.execute(stmt)
    models = results.scalars().all()

    items = [mapper(model) for model in models] if mapper else models

    return Page.create(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )
