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
    # Existing CHECK constraints require rebuilding events to admit the new type.
    # Keep IDs/watermarks intact; do not rename the old table (which rewrites FKs).
    old_event = connection.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()
    migrations = []
    columns = {r["name"] for r in connection.execute("PRAGMA table_info(tasks)")}
    if columns and "gap_type" not in columns:
        migrations.append("ALTER TABLE tasks ADD COLUMN gap_type TEXT;")
    if columns and "target_level" not in columns:
        declaration = schema.split("    target_level INTEGER", 1)[1].split(",\n    CHECK (status", 1)[0]
        migrations.append("ALTER TABLE tasks ADD COLUMN target_level INTEGER" + declaration + ";")
    rebuild = old_event is not None and "CAPABILITY_LEVEL_CHANGED" not in old_event["sql"]
    if rebuild:
        event_sql = schema.split("CREATE TABLE IF NOT EXISTS events (", 1)[1].split("\n);", 1)[0]
        migrations.extend([
            "CREATE TABLE events_progression (" + event_sql + "\n);",
            "INSERT INTO events_progression SELECT * FROM events;",
            "DROP TABLE events;",
            "ALTER TABLE events_progression RENAME TO events;"])
    foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    if rebuild:
        connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.executescript("BEGIN IMMEDIATE;\n" + "\n".join(migrations) + "\n" + schema)
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise sqlite3.IntegrityError("Migration would leave invalid foreign keys")
        connection.commit()
    except BaseException:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        if rebuild:
            connection.execute("PRAGMA foreign_keys = " + str(foreign_keys))


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
