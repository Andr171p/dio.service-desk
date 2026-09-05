from typing import Annotated

from fastapi import Depends, Query

from src.shared.application.dsl import Sort, parse_sort_from_query_param
from src.shared.application.dtos import Pagination


def get_sorting(
    sort: Annotated[
        str,
        Query(description="Сортировка по полю.", examples=["createdAt:desc", "-createdAt"])
    ],
) -> Sort:
    return parse_sort_from_query_param(sort)


PaginationDep = Annotated[Pagination, Depends(Query())]
SortDep = Annotated[Sort, Depends(get_sorting)]
