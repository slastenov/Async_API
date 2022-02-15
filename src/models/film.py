from typing import Optional, List, Dict

from .base import BaseApiModel


class Film(BaseApiModel):
    id: str
    title: str
    imdb_rating: float
    description: Optional[str] = ''
    actors: Optional[List[Dict]] = [{}]
    actors_names: Optional[List[str]] = ['']
    writers: Optional[List[Dict]] = [{}]
    writers_names: Optional[List[str]] = ['']
    directors_names: Optional[List[str]] = ['']
    directors: Optional[List[Dict]] = [{}]
    genre: Optional[List[str]] = ['']
    genres: Optional[List[Dict]] = [{}]


class FilmPerson(BaseApiModel):
    uuid: str
    title: str
    role: str
    imdb_rating: float
