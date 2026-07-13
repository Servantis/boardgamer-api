import os

from flask import Blueprint, jsonify, request

from services.sync_service import apply_sync_changes, get_changes_since


sync_bp = Blueprint("sync", __name__)


def _is_authorized() -> bool:
    expected_api_key = os.environ.get("BOARDGAMER_API_KEY")

    if not expected_api_key:
        return False

    provided_api_key = (
        request.headers.get("X-Api-Key")
        or request.headers.get("X-API-Key")
        or request.headers.get("x-api-key")
    )

    if not provided_api_key:
        return False

    return provided_api_key.strip() == expected_api_key.strip()


@sync_bp.before_request
def require_api_key():
    if not _is_authorized():
        return jsonify({
            "error": "Unauthorized",
            "message": "Missing or invalid X-Api-Key header."
        }), 401


@sync_bp.post("/push")
def push_changes():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400

    changes = data.get("changes")

    if not isinstance(changes, list):
        return jsonify({
            "error": "Invalid request",
            "message": "Property 'changes' must be a list."
        }), 400

    result = apply_sync_changes(changes)

    return jsonify(result)


@sync_bp.get("/pull")
def pull_changes():
    since = request.args.get("since")

    result = get_changes_since(since)

    return jsonify(result)