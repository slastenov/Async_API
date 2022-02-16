from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models.page import Page
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return Genre(uuid=genre.id, name=genre.name)


@router.get('/')
async def genre_list(
        page_size: int = Query(50, alias="page[size]", ge=1),
        page_number: int = Query(1, alias="page[number]", ge=1),
        genre_service: GenreService = Depends(get_genre_service),
) -> Page[Genre]:
    genres = await genre_service.get_list(page_size, page_number)
    if not genres.items:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    genres.items = [Genre(uuid=genre.id, name=genre.name) for genre in genres.items]
    return genres
