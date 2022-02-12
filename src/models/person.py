from typing import List

from .base import BaseApiModel
from .film import Film


class Person(BaseApiModel):
    id: str
    full_name: str
    roles: List[str] = []
    films: List[Film] = []
