from .base import BaseApiModel


class Film(BaseApiModel):
    id: str
    title: str
    description: str


class FilmPerson(BaseApiModel):
    uuid: str
    title: str
    role: str
    imdb_rating: float
