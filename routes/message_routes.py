import os

from flask import Blueprint, jsonify, request

from services.group_message_service import send_delay_message_to_group


message_bp = Blueprint("messages", __name__)


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


@message_bp.before_request
def require_api_key():
    if not _is_authorized():
        return jsonify({
            "error": "Unauthorized",
            "message": "Missing or invalid X-Api-Key header."
        }), 401


@message_bp.post("/delay")
def send_delay_message():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400

    group_id = data.get("group_id")
    sender_player_id = data.get("sender_player_id")
    delay_minutes = data.get("delay_minutes", 15)

    if not group_id:
        return jsonify({
            "error": "Validation error",
            "message": "group_id is required."
        }), 400

    if not sender_player_id:
        return jsonify({
            "error": "Validation error",
            "message": "sender_player_id is required."
        }), 400

    try:
        delay_minutes = int(delay_minutes)
    except ValueError:
        return jsonify({
            "error": "Validation error",
            "message": "delay_minutes must be a number."
        }), 400

    if delay_minutes < 1 or delay_minutes > 180:
        return jsonify({
            "error": "Validation error",
            "message": "delay_minutes must be between 1 and 180."
        }), 400

    try:
        result = send_delay_message_to_group(
            group_id=group_id,
            sender_player_id=sender_player_id,
            delay_minutes=delay_minutes
        )

        return jsonify(result)

    except Exception as ex:
        return jsonify({
            "error": "Message sending failed",
            "message": str(ex)
        }), 500