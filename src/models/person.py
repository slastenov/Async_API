from typing import List

from .base import BaseApiModel
from .film import FilmPerson


class Person(BaseApiModel):
    uuid: str
    full_name: str
    films: List[FilmPerson] = []
