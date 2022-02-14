def get_ids_list(data: list) -> tuple:
    """Обработка значений после извлечения из БД."""
    return tuple(column[0] for column in data)


def transform_data(data: list) -> list:
    """Подготовка данных для записи в ES после получения из БД, если не требуется каких-либо манипуляций данных с БД."""
    transformed_data = [dict(d) for d in data]
    return transformed_data
