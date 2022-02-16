from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import async_cache, get_redis
from models.genre import Genre
from models.page import Page

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 60  # 1 час


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @async_cache(Genre, False, GENRE_CACHE_EXPIRE_IN_SECONDS)
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_genre_from_elastic(genre_id)
        return genre

    @async_cache(Genre, True, GENRE_CACHE_EXPIRE_IN_SECONDS)
    async def get_list(self, page_size: int, page_number: int) -> Page:
        doc = await self.elastic.search(
            index="genres", size=page_size, from_=(page_number - 1) * page_size
        )
        return Page(
            items=[Genre(**d["_source"]) for d in doc["hits"]["hits"]],
            page_number=page_number,
            page_size=page_size,
            total=doc["hits"]["total"]["value"],
        )

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index="genres", id=genre_id)
        except exceptions.NotFoundError:
            return
        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
