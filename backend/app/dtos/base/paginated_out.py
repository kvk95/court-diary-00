from math import ceil
from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Paging(BaseModel):
    total_pages: int
    total_records: int
    size: int
    number: int
    number_of_elements: int
    first: bool
    last: bool


class PagingData(BaseModel, Generic[T]):
    paging: Paging
    records: List[T]


class PagingBuilder:
    def __init__(self, total_records: int, page: int, limit: int):
        self.total_records = total_records
        self.page = page
        self.limit = limit

    def build(self, records: List[T]) -> PagingData[T]:
        total_pages = ceil(self.total_records / self.limit) if self.limit else 0
        paging = Paging(
            total_pages=total_pages,
            total_records=self.total_records,
            size=self.limit,
            number=self.page,
            number_of_elements=len(records),
            first=(self.page == 1),
            last=(self.page >= total_pages),
        )
        return PagingData[T](paging=paging, records=records)
