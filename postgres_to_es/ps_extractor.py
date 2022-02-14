from typing import Generator

import backoff
import psycopg2
from psycopg2.extensions import connection as _connection
from queries import format_sql_for_ids


class PostgresExtractor:
    """Класс для выгрузки данных из postgres."""

    def __init__(self, pg_conn: _connection):
        self.connection = pg_conn
        self.batch_size = 100

    @backoff.on_exception(backoff.expo, psycopg2.OperationalError)
    def execute_query_generator(self, query: str, *args) -> Generator:
        """Выполнение sql запроса, метод возвращает генератор."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, args)

            while True:
                rows = cursor.fetchmany(size=self.batch_size)
                if not rows:
                    return
                yield rows

    @backoff.on_exception(backoff.expo, psycopg2.OperationalError)
    def execute_query(self, query: str, *args) -> list:
        """Выполнение запроса."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, args)

            return cursor.fetchall()

    def extract_updated_ids(self, table: str, last_date: str) -> Generator:
        """Получение генератора с id необновленных записей."""
        query = format_sql_for_ids(table)
        return self.execute_query_generator(query, (last_date,))
