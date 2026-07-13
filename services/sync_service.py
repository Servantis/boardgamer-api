import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from services.database_service import get_connection


ALLOWED_SYNC_TABLES = {
    "players",
    "player_devices",
    "gaming_groups",
    "group_members",
    "locations",
    "games",
    "game_nights",
    "attendance",
    "game_suggestions",
    "game_votes",
    "game_night_reviews",
}

ALLOWED_OPERATIONS = {
    "INSERT",
    "UPDATE",
    "DELETE",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def apply_sync_changes(changes: list[dict[str, Any]]) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    with get_connection() as connection:
        for change in changes:
            result = _apply_single_change(connection, change)

            if result["ok"]:
                accepted.append(result["entry"])
            else:
                rejected.append(result["entry"])

    return {
        "received_count": len(changes),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted": accepted,
        "rejected": rejected,
        "server_time": utc_now_iso(),
    }


def get_changes_since(since: str | None) -> dict[str, Any]:
    query = """
        SELECT
            id,
            entity_name,
            entity_id,
            operation,
            payload_json,
            created_at
        FROM server_change_log
    """

    parameters: tuple[Any, ...] = ()

    if since:
        query += " WHERE created_at > ?"
        parameters = (since,)

    query += " ORDER BY created_at ASC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    changes = []

    for row in rows:
        payload_json = row["payload_json"]

        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError:
            payload = None

        changes.append({
            "change_id": row["id"],
            "entity_name": row["entity_name"],
            "entity_id": row["entity_id"],
            "operation": row["operation"],
            "payload_json": payload_json,
            "payload": payload,
            "created_at": row["created_at"],
        })

    return {
        "server_time": utc_now_iso(),
        "since": since,
        "change_count": len(changes),
        "changes": changes,
    }


def _apply_single_change(connection: sqlite3.Connection, change: dict[str, Any]) -> dict[str, Any]:
    outbox_id = change.get("outbox_id") or change.get("id")
    entity_name = change.get("entity_name")
    entity_id = change.get("entity_id")
    operation = change.get("operation")

    if not entity_name:
        return _reject(outbox_id, entity_name, entity_id, operation, "entity_name fehlt.")

    if entity_name not in ALLOWED_SYNC_TABLES:
        return _reject(outbox_id, entity_name, entity_id, operation, f"Unbekannte oder nicht erlaubte Tabelle: {entity_name}")

    if not entity_id:
        return _reject(outbox_id, entity_name, entity_id, operation, "entity_id fehlt.")

    if operation not in ALLOWED_OPERATIONS:
        return _reject(outbox_id, entity_name, entity_id, operation, f"Ungültige Operation: {operation}")

    try:
        payload = _extract_payload(change)

        if payload is None:
            return _reject(outbox_id, entity_name, entity_id, operation, "Payload fehlt oder ist ungültig.")

        payload["id"] = entity_id

        if operation == "DELETE":
            _apply_delete(connection, entity_name, entity_id, payload)
        else:
            _apply_upsert(connection, entity_name, payload)

        _insert_server_change_log(
            connection=connection,
            entity_name=entity_name,
            entity_id=entity_id,
            operation=operation,
            payload=payload,
        )

        connection.commit()

        return {
            "ok": True,
            "entry": {
                "outbox_id": outbox_id,
                "entity_name": entity_name,
                "entity_id": entity_id,
                "operation": operation,
                "status": "accepted",
            }
        }

    except sqlite3.IntegrityError as exception:
        connection.rollback()

        return _reject(
            outbox_id,
            entity_name,
            entity_id,
            operation,
            f"SQLite IntegrityError: {exception}"
        )

    except Exception as exception:
        connection.rollback()

        return _reject(
            outbox_id,
            entity_name,
            entity_id,
            operation,
            f"Fehler beim Anwenden der Änderung: {exception}"
        )


def _extract_payload(change: dict[str, Any]) -> dict[str, Any] | None:
    if "payload" in change and isinstance(change["payload"], dict):
        return change["payload"]

    payload_json = change.get("payload_json")

    if not payload_json:
        return None

    if isinstance(payload_json, dict):
        return payload_json

    if isinstance(payload_json, str):
        return json.loads(payload_json)

    return None


def _apply_upsert(connection: sqlite3.Connection, table_name: str, payload: dict[str, Any]) -> None:
    table_columns = _get_table_columns(connection, table_name)

    filtered_payload = {
        key: value
        for key, value in payload.items()
        if key in table_columns
    }

    if "id" not in filtered_payload:
        raise ValueError("Payload enthält keine id.")

    columns = list(filtered_payload.keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)

    update_columns = [column for column in columns if column != "id"]

    if update_columns:
        update_statement = ", ".join([
            f"{column} = excluded.{column}"
            for column in update_columns
        ])
    else:
        update_statement = "id = excluded.id"

    sql = f"""
        INSERT INTO {table_name} ({column_list})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET
            {update_statement};
    """

    values = tuple(filtered_payload[column] for column in columns)

    connection.execute(sql, values)


def _apply_delete(
    connection: sqlite3.Connection,
    table_name: str,
    entity_id: str,
    payload: dict[str, Any]
) -> None:
    deleted_at = payload.get("deleted_at") or utc_now_iso()
    updated_at = payload.get("updated_at") or deleted_at
    version = payload.get("version")

    existing = connection.execute(
        f"SELECT id, version FROM {table_name} WHERE id = ?",
        (entity_id,)
    ).fetchone()

    if existing is None:
        raise ValueError(f"Datensatz für DELETE nicht gefunden: {table_name}/{entity_id}")

    if version is None:
        version = int(existing["version"]) + 1

    connection.execute(
        f"""
        UPDATE {table_name}
        SET deleted_at = ?,
            updated_at = ?,
            version = ?
        WHERE id = ?;
        """,
        (deleted_at, updated_at, version, entity_id)
    )

    payload["deleted_at"] = deleted_at
    payload["updated_at"] = updated_at
    payload["version"] = version


def _insert_server_change_log(
    connection: sqlite3.Connection,
    entity_name: str,
    entity_id: str,
    operation: str,
    payload: dict[str, Any]
) -> None:
    connection.execute(
        """
        INSERT INTO server_change_log (
            id,
            entity_name,
            entity_id,
            operation,
            payload_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            str(uuid4()),
            entity_name,
            entity_id,
            operation,
            json.dumps(payload, ensure_ascii=False),
            utc_now_iso(),
        )
    )


def _get_table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name});").fetchall()
    return {row["name"] for row in rows}


def _reject(
    outbox_id: str | None,
    entity_name: str | None,
    entity_id: str | None,
    operation: str | None,
    reason: str
) -> dict[str, Any]:
    return {
        "ok": False,
        "entry": {
            "outbox_id": outbox_id,
            "entity_name": entity_name,
            "entity_id": entity_id,
            "operation": operation,
            "status": "rejected",
            "reason": reason,
        }
    }