from typing import Optional

from .base import BaseApiModel


class Genre(BaseApiModel):
    id: str
    name: str
    description: Optional[str] = ""
