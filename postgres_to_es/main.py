import logging

import psycopg2
from config import ElasticSearchSettings, PostgresSettings
from es_loader import ElasticSearchLoader

from psycopg2.extras import DictCursor
from etl_process import MoviesETLProcessor, PersonETLProcessor, GenresETLProcessor


logger = logging.getLogger(__name__)


def etl():
    """Основной процесс получения данных."""
    logger.info("Start")

    ps_conn = PostgresSettings()
    es_conn = ElasticSearchSettings()
    es = ElasticSearchLoader(es_conn.dict())
    with psycopg2.connect(**ps_conn.dict(), cursor_factory=DictCursor) as pg_conn:
        etl_movies = MoviesETLProcessor(es, pg_conn)
        etl_movies.process()
        etl_persons = PersonETLProcessor(es, pg_conn)
        etl_persons.process()
        etl_genres = GenresETLProcessor(es, pg_conn)
        etl_genres.process()


if __name__ == "__main__":
    etl()
