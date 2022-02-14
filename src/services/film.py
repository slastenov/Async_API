from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.base import Page
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def search(self, query: str, page: int, size: int) -> Page[Film]:
        result = await self._search_film_from_elastic(query, page, size)
        return result

    async def _search_film_from_elastic(self, query: str, page: int, size: int) -> Page[Film]:
        body = """
            {
                "query": {
                    "multi_match": {
                        "query": "%s",
                        "fields": [
                            "title^3",
                            "description"
                        ],
                        "operator": "and",
                        "fuzziness": "AUTO"
                    }
                },
                "from": %s,
                "size": %s
            }
        """ % (query, (page - 1) * size, size)
        doc = await self.elastic.search(index="movies", body=body)
        return Page(
            items=[Film(**film['_source']) for film in doc["hits"]["hits"]],
            page=page,
            size=size,
            total=doc['hits']['total']['value'],
        )

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except exceptions.NotFoundError:
            return
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
