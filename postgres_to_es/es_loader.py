import json
import logging

import backoff
from elasticsearch import Elasticsearch, TransportError
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)


class ElasticSearchLoader:
    """Класс загрузки данных в ElasticSearch."""

    def __init__(self, connection: dict):
        self.es = Elasticsearch([connection])

    @backoff.on_exception(backoff.expo, TransportError)
    def create_index(self, index_name, index_scheme) -> None:
        """Создание индекса в ES."""

        if not self.es.indices.exists(index=index_name):
            with open(index_scheme) as fp:
                index_body = json.load(fp)
            self.es.indices.create(index=index_name, body=index_body)
            logger.info("Created index %s", index_name)

    @backoff.on_exception(backoff.expo, TransportError)
    def load_es_data(self, data: list, index_name) -> None:
        """Загрузка данных в ES."""

        bulk(self.es, data, index=index_name)
