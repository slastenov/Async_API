import logging

import psycopg2
from psycopg2.extras import DictCursor

from config import PostgresSettings, ElasticSearchSettings
from es_loader import ElasticSearchLoader
from etl_process import MoviesETLProcessor

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


if __name__ == '__main__':
    etl()
