from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

from models.base import Page

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float


class FilmDetail(BaseModel):
    id: str
    title: str
    imdb_rating: float
    description: Optional[str] = ''
    actors: List[dict]
    writers: List[dict]
    directors: List[dict]
    genre: List[dict]


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetail(id=film.id,
                      title=film.title,
                      imdb_rating=film.imdb_rating,
                      description=film.description,
                      actors=film.actors,
                      writers=film.writers,
                      directors=film.director,
                      genre=film.genre,
                      )


@router.get(path='/search/', response_model=Page[Film])
async def film_search(
        query: str,
        page: int,
        size: int,
        film_service: FilmService = Depends(get_film_service),
) -> Page[Film]:
    page = await film_service.search(query, page, size)
    return page
