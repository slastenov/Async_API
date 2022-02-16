from typing import Generic, List, TypeVar

from pydantic import Field

from models.base import BaseApiModel

ElasticModel = TypeVar("ElasticModel")


class Page(BaseApiModel, Generic[ElasticModel]):
    """Страница результатов с пагинацией."""

    items: List[ElasticModel] = Field(
        default=[],
        title="List of objects",
    )
    page_number: int = Field(
        title="Page number",
        default=1,
        example=1,
    )
    page_size: int = Field(
        title="Amount of items on page",
        default=20,
        example=20,
    )
    total: int = Field(
        title="Total items",
        example=35,
    )
