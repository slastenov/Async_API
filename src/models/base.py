from pydantic import BaseModel

import orjson


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseApiModel(BaseModel):
    """Базовый класс для моделей API."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
