from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 60  # 1 час


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_list(self) -> Optional[List[Person]]:
        resp = await self.elastic.search(index="person", size=500)
        persons = [Person(**doc["_source"]) for doc in resp["hits"]["hits"]]
        return persons

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="person", id=person_id)
        except exceptions.NotFoundError:
            return
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            person.uuid, person.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
