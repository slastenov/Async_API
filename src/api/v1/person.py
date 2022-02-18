from http import HTTPStatus
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from models.page import Page
from models.person import ResponsePerson, ResponsePersonFilms
from models.constants import PERSON_NOT_FOUND
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/{person_id}", response_model=ResponsePerson)
async def person_details(
        person_id: str, person_service: PersonService = Depends(get_person_service)
) -> ResponsePerson:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return ResponsePerson(**person.dict())


@router.get("/{person_id}/film", response_model=ResponsePersonFilms)
async def person_film_details(
        person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Dict[str, Any]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_NOT_FOUND)

    return person.dict()


@router.get(path="/search/", response_model=Page[ResponsePerson])
async def film_search(
        query: str,
        page_number: int = Query(1, alias="page[number]", ge=1),
        page_size: int = Query(50, alias="page[size]", ge=1),
        person_service: PersonService = Depends(get_person_service),
) -> Page[ResponsePerson]:
    page = await person_service.search(query, page_size, page_number)
    page.items = [
        ResponsePerson(uuid=person.uuid, full_name=person.full_name, films=person.films)
        for person in page.items
    ]

    return page
