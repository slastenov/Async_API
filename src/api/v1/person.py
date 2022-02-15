from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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


@router.get("/")
async def person_list(
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    persons = await person_service.get_list()
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return [Person(**person.dict()) for person in persons]
