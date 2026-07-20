import os
import sqlite3
from pathlib import Path

from services.mailtrap_service import send_email_with_mailtrap


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "database" / "boardgamer.db"


def _get_db_path() -> str:
    return os.environ.get("BOARDGAMER_DATABASE_PATH", str(DEFAULT_DB_PATH))


def _connect():
    connection = sqlite3.connect(_get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def send_delay_message_to_group(
    group_id: str,
    sender_player_id: str,
    delay_minutes: int
) -> dict:
    with _connect() as connection:
        sender = connection.execute(
            """
            SELECT id, name
            FROM players
            WHERE id = ?
              AND deleted_at IS NULL
              AND is_active = 1;
            """,
            (sender_player_id,)
        ).fetchone()

        if sender is None:
            raise RuntimeError("Der sendende Spieler wurde nicht gefunden.")

        group = connection.execute(
            """
            SELECT id, name
            FROM gaming_groups
            WHERE id = ?
              AND deleted_at IS NULL;
            """,
            (group_id,)
        ).fetchone()

        if group is None:
            raise RuntimeError("Die Spielgruppe wurde nicht gefunden.")

        recipients = connection.execute(
            """
            SELECT DISTINCT p.email
            FROM group_members gm
            JOIN players p ON p.id = gm.player_id
            WHERE gm.group_id = ?
              AND gm.player_id <> ?
              AND gm.status = 'active'
              AND gm.deleted_at IS NULL
              AND p.deleted_at IS NULL
              AND p.is_active = 1
              AND p.email IS NOT NULL
              AND TRIM(p.email) <> ''
            ORDER BY p.email;
            """,
            (group_id, sender_player_id)
        ).fetchall()

    recipient_emails = [row["email"] for row in recipients]

    if not recipient_emails:
        raise RuntimeError("Für diese Gruppe wurden keine Empfänger-E-Mail-Adressen gefunden.")

    sender_name = sender["name"]
    group_name = group["name"]

    subject = f"Verspätung zum Spieleabend - {group_name}"

    text = (
        f"Hallo zusammen,\n\n"
        f"{sender_name} verspätet sich leider und kommt voraussichtlich "
        f"ca. {delay_minutes} Minuten später.\n\n"
        f"Viele Grüße\n"
        f"BoardGamer App"
    )

    mailtrap_response = send_email_with_mailtrap(
        recipients=recipient_emails,
        subject=subject,
        text=text,
        category="boardgamer_delay_message"
    )

    return {
        "status": "sent",
        "group_id": group_id,
        "sender_player_id": sender_player_id,
        "recipient_count": len(recipient_emails),
        "mailtrap_response": mailtrap_response
    }