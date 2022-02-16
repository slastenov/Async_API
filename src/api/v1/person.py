from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models.page import Page
from models.person import FilmPerson
from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str
    films: List[FilmPerson] = []


class PersonFilms(BaseModel):
    films: List[FilmPerson] = []


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return Person(**person.dict())


@router.get("/{person_id}/film", response_model=PersonFilms)
async def person_film_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonFilms:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person.dict()


@router.get(path='/search/', response_model=Page[Person])
async def film_search(
        query: str,
        page_number: int = Query(1, alias="page[number]", ge=1),
        page_size: int = Query(50, alias="page[size]", ge=1),
        person_service: PersonService = Depends(get_person_service),
) -> Page[Person]:
    page = await person_service.search(query, page_size, page_number)
    page.items = [Person(uuid=person.uuid, full_name=person.full_name, films=person.films) for person in page.items]

    return page
