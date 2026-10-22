"""Database connection and query helpers for the backend.

This module wraps raw psycopg calls so the rest of the application can issue
simple SQL statements without repeated connection and cursor boilerplate.
"""

import psycopg
from psycopg.rows import dict_row, tuple_row

from config import DB_URI


def get_con(row_factory=dict_row) -> psycopg.Connection:
    """Create and return a PostgreSQL connection configured with the chosen row factory.

    Args:
        row_factory: A psycopg row factory used to translate database rows into
            Python dictionaries or tuples.

    Returns:
        A live psycopg connection object.
    """
    return psycopg.connect(DB_URI, row_factory=row_factory)



def sql(
    query: str,
    as_dict: bool = True,
    fetch_one: bool = False,
    params: list | tuple | dict | None = None,
    execute_many: bool = False,
):
    """Execute a SQL statement and optionally return one or many rows.

    Args:
        query: The SQL text to execute.
        as_dict: If True, rows are returned as dictionaries; otherwise tuples.
        fetch_one: When True, return a single row instead of a list.
        params: Query parameters for a normal statement or executemany call.
        execute_many: If True, run the query once per item in params.

    Returns:
        The result of the SQL execution, usually a row dict, a list of row dicts,
        or None when no data is returned.
    """
    row_factory = dict_row if as_dict else tuple_row
    with get_con(row_factory=row_factory) as con:
        with con.cursor() as cursor:
            if execute_many:
                # executemany is used for bulk insert patterns where the same query is
                # re-used for multiple rows, such as batch person imports.
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchone() if fetch_one else cursor.fetchall()