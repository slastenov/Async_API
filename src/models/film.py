from typing import Optional, List, Dict

from .base import BaseApiModel


class Film(BaseApiModel):
    id: str
    title: str
    imdb_rating: float
    description: Optional[str] = ''
    actors: List[Dict] = [{}]
    actors_names: List[str] = ['']
    writers: List[Dict] = [{}]
    writers_names: List[str] = ['']
    director: List[str]
    genre: List[str]
    genres: List[Dict]


class FilmPerson(BaseApiModel):
    uuid: str
    title: str
    role: str
    imdb_rating: float
