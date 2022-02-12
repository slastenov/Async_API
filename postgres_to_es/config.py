import logging

from pydantic import BaseSettings, Field
from pydantic.env_settings import SettingsSourceCallable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class EnvPrioritySettings(BaseSettings):
    class Config:
        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> tuple:
            return env_settings, init_settings, file_secret_settings


class PostgresSettings(EnvPrioritySettings):
    """Валидация для подключения к Postgres."""
    host: str = Field(..., env='POSTGRES_HOST')
    port: str = Field(..., env='POSTGRES_PORT')
    dbname: str = Field(..., env='POSTGRES_DB')
    password: str = Field(..., env='POSTGRES_PASSWORD')
    user: str = Field(..., env='POSTGRES_USER')
    options: str = "-c search_path=content"


class ElasticSearchSettings(EnvPrioritySettings):
    """Валидация для подключения к ElasticSearch."""
    host: str = Field(..., env='ELASTIC_HOST')
    port: str = Field(..., env='ELASTIC_PORT')
