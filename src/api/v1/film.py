from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models.page import Page
from models.film import ResponseFilm, ResponseFilmDetail
from models.constants import FILM_NOT_FOUND
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/{film_id}", response_model=ResponseFilmDetail)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> ResponseFilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return ResponseFilmDetail(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get(path="/search/", response_model=Page[ResponseFilm])
async def film_search(
    query: str,
    page_number: int = Query(1, alias="page[number]", ge=1),
    page_size: int = Query(50, alias="page[size]", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> Page[ResponseFilm]:
    page = await film_service.search(query, page_number, page_size)
    page.items = [
        ResponseFilm(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
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
) -> Page[ResponseFilm]:
    page = await film_service.get_list(sort, page_size, page_number, filter_genre)
    page.items = [
        ResponseFilm(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in page.items
    ]
    return page
