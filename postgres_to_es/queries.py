from psycopg2 import sql


def format_sql_for_ids(table_name: str):
    """Запрос для получения id новых записей."""
    query = sql.SQL("select id from {table} where updated_at >= %s order by updated_at;") \
        .format(table=sql.Identifier(table_name))
    return query


def format_sql_for_related_filmwork(table_name: str, column_name: str):
    """Запрос для получения id кинопроизведений из связанных таблиц."""
    related_filmwork_ids = sql.SQL("""select fw.id from film_work fw 
    left join {table} on {table}.film_work_id = fw.id 
    where {column} in %s order by fw.updated_at;""") \
        .format(table=sql.Identifier(table_name), column=sql.Identifier(table_name, column_name))
    return related_filmwork_ids


def format_sql_for_all_filmworks():
    """Запрос для получения данных кинопроизведений."""
    all_filmworks = """
    select 
        fw.id as _id,
        fw.id,
        fw.title,
        fw.description,
        fw.rating as imdb_rating,
        array_agg(distinct p.full_name ) filter ( where pfw.role = 'director' ) as director,
        array_agg(distinct p.full_name) filter ( where pfw.role = 'actor' ) as actors_names,
        array_agg(distinct p.full_name) filter ( where pfw.role = 'writer' ) as writers_names,
        json_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) 
            filter ( where pfw.role = 'actor' ) as actors,
        json_agg(distinct jsonb_build_object('id', p.id, 'name', p.full_name)) 
            filter ( where pfw.role = 'writer' ) as writers,
        array_agg(distinct g.name ) as genre
    from film_work fw 
        left join person_film_work pfw on pfw.film_work_id = fw.id
        left join person p on p.id = pfw.person_id
        left join genre_film_work gfw on gfw.film_work_id = fw.id
        left join genre g on g.id = gfw.genre_id
     where fw.id in %s
     group by fw.id
     order by fw.id;"""
    return all_filmworks