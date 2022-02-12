from typing import List

from .base import BaseApiModel
from .film import Film


class GenreDetailed(BaseApiModel):
    id: str
    name: str
    description: str
    films: List[Film] = []
