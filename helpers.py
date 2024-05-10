import contextlib
import sys
import time

import mysql.connector
from rich.progress import track
from rich.table import Table


def create_table(
    items: list, server_name="", table_collapse=False, table_highlight=False
):
    table = Table(
        title=f"MySQL process list - {server_name}" if server_name else None,
        collapse_padding=table_collapse,
        highlight=table_highlight,
    )

    for key in items[0].keys():
        table.add_column(key)

    for item in items:
        table.add_row(*[str(value) for value in item.values()])

    return table


@contextlib.contextmanager
def get_mysql_conn(
    host: str,
    user: str,
    password: str,
    db: str,
    port: int = 3306,
    timeout: int = 10,
    autocommit: bool = False,
    buffered: bool = False,
):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        port=port,
        connection_timeout=timeout,
        autocommit=autocommit,
        buffered=buffered,
    )

    try:
        yield conn
    finally:
        conn.close()


def bar_progress(seconds: int, description: str = "Working..."):
    try:
        for i in track(range(seconds), description=description):
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
