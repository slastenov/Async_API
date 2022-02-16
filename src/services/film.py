from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import async_cache, get_redis
from models.film import Film
from models.page import Page

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 60


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @async_cache(Film, page=False, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._get_film_from_elastic(film_id)
        return film

    @async_cache(Film, page=True, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
    async def get_list(
        self, sort: str, page_size: int, page_number: int, filter_genre: str
    ) -> Page[Film]:
        result = await self._get_list_from_elastic(
            sort, page_number, page_size, filter_genre
        )
        return result

    @async_cache(Film, page=True, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
    async def search(self, query: str, page_number: int, page_size: int) -> Page[Film]:
        result = await self._search_film_from_elastic(query, page_number, page_size)
        return result

    async def _get_list_from_elastic(
        self, sort: str, page_number: int, page_size: int, filter_genre: str
    ) -> Page[Film]:
        order = "asc"
        if sort.startswith("-"):
            order = "desc"
            sort = sort[1:]

        body = {"sort": {sort: {"order": order}}}

        if filter_genre:
            body["query"] = {
                "bool": {
                    "filter": {
                        "nested": {
                            "path": "genres",
                            "query": {
                                "bool": {
                                    "filter": {"term": {"genres.id": filter_genre}}
                                }
                            },
                        }
                    }
                }
            }
        return await self._get_pages_from_elastic(body, page_number, page_size)

    async def _search_film_from_elastic(
        self, query: str, page_number: int, page_size: int
    ) -> Page[Film]:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description"],
                    "operator": "and",
                    "fuzziness": "AUTO",
                }
            }
        }
        return await self._get_pages_from_elastic(body, page_number, page_size)

    async def _get_pages_from_elastic(
        self, body: dict, page_number: int, page_size: int
    ) -> Page[Film]:
        body["from"] = (page_number - 1) * page_size
        body["size"] = page_size

        doc = await self.elastic.search(index="movies", body=body)

        return Page(
            items=[Film(**film["_source"]) for film in doc["hits"]["hits"]],
            page_number=page_number,
            page_size=page_size,
            total=doc["hits"]["total"]["value"],
        )

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except exceptions.NotFoundError:
            return
        return Film(**doc["_source"])


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
