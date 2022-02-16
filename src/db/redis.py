from functools import wraps
from typing import Optional, Type, Callable

from aioredis import Redis

from models.base import BaseApiModel
from models.page import Page


redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis


def async_cache(model: Type[BaseApiModel] = None, page: bool = False, ttl: int = 60) -> Callable:
    def _cache(fn):
        @wraps(fn)
        async def _wrapper(*args, **kwargs):
            using_model = Page[model] if page else model

            key_args = "|".join(str(a) for a in args[1:])
            key_kwargs = "|".join(f"{k}={v}" for k, v in kwargs.items())
            key = f"{model.__name__}|{fn.__name__}|{key_args}|{key_kwargs}"
            data = await redis.get(key)
            if data:
                data = using_model.parse_raw(data)
                if page:
                    data.items = [model(**d) for d in data.items]
            else:
                data = await fn(*args, **kwargs)
                if data:
                    await redis.set(key, data.json(), expire=ttl)

            return data

        return _wrapper

    return _cache
