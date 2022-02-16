from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models.page import Page
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class FilmDetail(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    description: Optional[str] = ""
    genre: Optional[List[dict]] = []
    actors: Optional[List[dict]] = []
    writers: Optional[List[dict]] = []
    directors: Optional[List[dict]] = []


@router.get("/{film_id}", response_model=FilmDetail)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetail(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get(path="/search/", response_model=Page[Film])
async def film_search(
    query: str,
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(50, alias="page[size]", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> Page[Film]:
    page = await film_service.search(query, page_number, page_size)
    page.items = [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in page.items
    ]

    return page


@router.get("/")
async def film_list(
    sort: Optional[str] = "-imdb_rating",
    page_size: int = Query(50, alias="page[size]", ge=1),
    page_number: int = Query(1, alias="page[number]", ge=1),
    filter_genre: str = Query(None, alias="filter[genre]"),
    film_service: FilmService = Depends(get_film_service),
) -> Page[Film]:
    page = await film_service.get_list(sort, page_size, page_number, filter_genre)
    page.items = [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in page.items
    ]
    return page
