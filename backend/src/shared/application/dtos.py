from typing import Annotated, Any, Self

from collections.abc import Callable

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt

from .dsl import Filter


class Pagination(BaseModel):
    """Параметры пагинации, которые приходят от клиента (query config)."""

    page: PositiveInt = Field(
        default=1,
        ge=1,
        description="Номер страницы, начинается с 1",
    )
    size: PositiveInt = Field(
        default=10,
        ge=1,
        le=100,
        description="Размер страницы (количество элементов на странице)."
    )

    @property
    def offset(self) -> int:
        """Смещение пагинации"""

        return (self.page - 1) * self.size


class Page[T: Any](BaseModel):
    """Полная страница с элементами."""

    page: PositiveInt = Field(description="Текущий номер страницы")
    size: PositiveInt = Field(description="Количество элементов на странице")
    total: NonNegativeInt = Field(description="Всего элементов на сервере")
    pages: NonNegativeInt = Field(description="Всего страниц")
    has_next: bool = Field(description="Есть ли следующая страница")
    has_prev: bool = Field(description="Есть ли предыдущая страница")
    items: list[T] = Field(default_factory=list, description="Полученные элементы")

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> Self:
        total_pages = (total + size - 1) // size

        has_next = page * size < total
        has_prev = page > 1

        return Page(
            page=page,
            size=size,
            total=total,
            pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            items=items,
        )

    def to_response[R: BaseModel](self, mapper: Callable[[T], R]) -> "Page[R]":
        """Преобразование страницы к ResponseDTO."""

        return Page(
            page=self.page,
            size=self.size,
            total=self.total,
            pages=self.pages,
            has_next=self.has_next,
            has_prev=self.has_prev,
            items=[mapper(item) for item in self.items],
        )


QueryDTO = Annotated[Filter, Field(description="DTO для построения фильтров через DSL.")]
