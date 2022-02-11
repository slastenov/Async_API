def get_ids_list(data: list) -> tuple:
    """Обработка значений после извлечения из БД."""
    return tuple(column[0] for column in data)


def transform_movies(movies: list) -> list:
    """Подготовка кинопроизведений для записи в ES после получения из БД."""
    transformed_data = [dict(movie) for movie in movies]
    return transformed_data
