import os
from flask import Blueprint, jsonify

from services.database_service import fetch_one, get_database_path


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    database_ok = True
    database_error = None

    try:
        result = fetch_one("SELECT COUNT(*) AS player_count FROM players;")
        player_count = result["player_count"] if result else 0
    except Exception as exception:
        database_ok = False
        database_error = str(exception)
        player_count = None

    api_key = os.environ.get("BOARDGAMER_API_KEY")

    return jsonify({
        "status": "ok",
        "service": "boardgamer-api",
        "api_key_configured": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,
        "database": {
            "ok": database_ok,
            "path": str(get_database_path()),
            "player_count": player_count,
            "error": database_error
        }
    })