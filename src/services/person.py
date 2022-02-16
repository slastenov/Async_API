from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis, async_cache
from models.page import Page
from models.person import Person

GENRE_PERSON_EXPIRE_IN_SECONDS = 60 * 60  # 1 час


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @async_cache(Person, page=False, ttl=GENRE_PERSON_EXPIRE_IN_SECONDS)
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_from_elastic(person_id)
        return person

    @async_cache(Person, page=True, ttl=GENRE_PERSON_EXPIRE_IN_SECONDS)
    async def search(self, query: str, page_size: int, page_number: int) -> Page[Person]:
        body = {
            "multi_match": {
                "query": query,
                "fields": [
                    "full_name^3",
                ],
                "operator": "and",
                "fuzziness": "AUTO"
            }
        }
        start_page = (page_number - 1) * page_size
        doc = await self.elastic.search(index='person', query=body, size=page_size, from_=start_page)
        return Page(
            items=[Person(**person["_source"]) for person in doc["hits"]["hits"]],
            page_number=page_number,
            page_size=page_size,
            total=doc["hits"]["total"]["value"],
        )

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="person", id=person_id)
        except exceptions.NotFoundError:
            return
        return Person(**doc["_source"])


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
