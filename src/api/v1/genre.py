from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return Genre(id=genre.id, name=genre.name)


@router.get('/')
async def genre_list(genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    genres_list = [Genre(id=genre.id, name=genre.name) for genre in genres]
    return genres_list
