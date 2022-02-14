import abc
import logging
from datetime import datetime
from typing import Generator

from ps_extractor import PostgresExtractor
from queries import (format_sql_for_all_filmworks, format_sql_for_all_persons,
                     format_sql_for_related_filmwork,
                     format_sql_for_related_person)
from state import JsonFileStorage, State
from transformer import get_ids_list, transform_data

logger = logging.getLogger(__name__)


class ETLProcessor(abc.ABC):
    """
    Абстрактный класс для построения ETL процесса.
    Класс-наследник строится под каждую схему.
    """

    index_scheme: str
    index_name: str
    tables: dict
    state_file: str

    def __init__(self, es, pg_connection):
        self.es = es
        self.extractor = PostgresExtractor(pg_connection)
        self.state_storage = State(JsonFileStorage(self.state_file))

    def process(self):
        """Метод для переноса данных."""
        logger.info("Checking available indexes")
        self.es.create_index(self.index_name, self.index_scheme)
        logger.info("Grabbing data")
        for table, related in self.tables.items():
            last_date = self.state_storage.get_state(table) or datetime.min

            for updated_ids in self.extractor.extract_updated_ids(table, last_date):

                updated_ids_list = get_ids_list(updated_ids)
                if related:
                    updated_ids = self.extract_related_ids(*related, updated_ids_list)
                    updated_ids_list = get_ids_list(updated_ids)
                for data in self.extract_all_data(updated_ids_list):
                    transformed_data = self.transform_data(data)
                    self.es.load_es_data(transformed_data, self.index_name)

            self.state_storage.set_state(
                table, datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
            )
            logger.info("New data added from table %s", table)
        logger.info("New data added to index %s", self.index_name)

    @abc.abstractmethod
    def extract_related_ids(self, table: str, column: str, related_ids: tuple) -> list:
        """Метод получения данных из зависимых таблиц."""
        pass

    @abc.abstractmethod
    def extract_all_data(self, ids: tuple) -> Generator:
        """Метод получения всех необходимых данных."""
        pass

    @abc.abstractmethod
    def transform_data(self, data: list) -> list:
        """Метод для изменения данных под нужную схему."""
        pass


class MoviesETLProcessor(ETLProcessor):
    """Конкретный класс для заполнения данных по схеме movies."""

    index_name = "movies"
    index_scheme = f"es_indexes/{index_name}.json"
    tables = {
        "film_work": None,
        "genre": ("genre_film_work", "genre_id"),
        "person": ("person_film_work", "person_id"),
    }
    state_file = "state/film_state.json"

    def extract_related_ids(self, table: str, column: str, related_ids: tuple) -> list:
        """Извлечение идентификаторов через связующую таблицу."""
        query = format_sql_for_related_filmwork(table, column)
        return self.extractor.execute_query(query, related_ids)

    def extract_all_data(self, ids: tuple) -> Generator:
        """Извлечение данных о кинолентах по кортежу с id."""
        query = format_sql_for_all_filmworks()
        return self.extractor.execute_query_generator(query, ids)

    def transform_data(self, data: list) -> list:
        """Изменение данных под схему movies"""
        return transform_data(data)


class PersonETLProcessor(ETLProcessor):
    """Конкретный класс для заполнения данных по схеме person."""

    index_name = "person"
    index_scheme = f"es_indexes/{index_name}.json"
    tables = {
        "person": None,
        "film_work": ("person_film_work", "person_id"),
    }
    state_file = "state/person_state.json"

    def extract_related_ids(self, table: str, column: str, related_ids: tuple) -> list:
        """Извлечение идентификаторов через связующую таблицу."""
        query = format_sql_for_related_person(table, column)
        return self.extractor.execute_query(query, related_ids)

    def extract_all_data(self, ids: tuple) -> Generator:
        """Извлечение данных о персонах по кортежу с id."""
        query = format_sql_for_all_persons()
        return self.extractor.execute_query_generator(query, ids)

    def transform_data(self, data: list) -> list:
        """Изменение данных под схему person."""
        return transform_data(data)
