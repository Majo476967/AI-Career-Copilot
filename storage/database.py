"""Explicit connections and transactions; importing this module creates no database."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "runtime" / "career_copilot.sqlite3"


def connect_database(path=DEFAULT_DATABASE_PATH):
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA recursive_triggers = ON")
    return connection


def initialize_database(connection):
    if connection.in_transaction:
        raise RuntimeError("Initialize outside a business transaction")
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    try:
        connection.executescript("BEGIN IMMEDIATE;\n" + schema + "\nCOMMIT;")
    except BaseException:
        if connection.in_transaction:
            connection.rollback()
        raise


@contextmanager
def transaction(connection):
    """Group repository writes and event appends atomically. No implicit nesting."""
    if connection.in_transaction:
        raise RuntimeError("Nested transactions are not supported")
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
