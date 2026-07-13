import os
import sqlite3
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_DB_PATH = BASE_DIR / "database" / "boardgamer.db"
DEFAULT_SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_database_path() -> Path:
    configured_path = os.environ.get("BOARDGAMER_DB_PATH")

    if configured_path:
        return Path(configured_path).expanduser().resolve()

    return DEFAULT_DB_PATH


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def initialize_database(schema_path: Path | None = None) -> None:
    selected_schema_path = schema_path or DEFAULT_SCHEMA_PATH

    if not selected_schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {selected_schema_path}")

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        schema_sql = selected_schema_path.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
        connection.commit()


def fetch_all(query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def fetch_one(query: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(query, parameters).fetchone()

        if row is None:
            return None

        return dict(row)


def execute(query: str, parameters: tuple[Any, ...] = ()) -> int:
    with get_connection() as connection:
        cursor = connection.execute(query, parameters)
        connection.commit()
        return cursor.rowcount


def execute_many(query: str, parameters: list[tuple[Any, ...]]) -> int:
    with get_connection() as connection:
        cursor = connection.executemany(query, parameters)
        connection.commit()
        return cursor.rowcount