import abc
import json
from pathlib import Path
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or "state/state.json"

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        data = self.retrieve_state()
        data.update(state)
        with open(self.file_path, "w") as fp:
            json.dump(data, fp, ensure_ascii=False)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        try:
            file = Path(self.file_path)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch(exist_ok=True)
            with open(self.file_path, "r") as fp:
                return json.load(fp)
        except json.JSONDecodeError:
            return dict()


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state().get(key)
