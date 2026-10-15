import psycopg
from psycopg.rows import dict_row, tuple_row
from backend.config import DB_URI

def get_con(row_factory = dict_row) -> psycopg.Connection:
    try:
        return psycopg.connect(DB_URI, row_factory = row_factory)
    except: 
        raise

def sql(
        query: str, 
        as_dict: bool = True, 
        fetch_one: bool = False, 
        params: list | tuple | dict | None = None, 
        execute_many: bool = False
    ):
    row_factory = dict_row if as_dict else tuple_row
    with get_con(row_factory = row_factory) as con:
        with con.cursor() as cursor:
            if execute_many:
                cursor.executemany(query, params) 
            else:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchone() if fetch_one else cursor.fetchall()