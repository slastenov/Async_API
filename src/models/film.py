from .base import BaseApiModel


class Film(BaseApiModel):
    id: str
    title: str
    description: str
