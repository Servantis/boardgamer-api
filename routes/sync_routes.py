from flask import Blueprint, jsonify, request

sync_bp = Blueprint("sync", __name__)


@sync_bp.post("/push")
def push_changes():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    changes = data.get("changes", [])

    return jsonify({
        "accepted": [],
        "rejected": [],
        "received_count": len(changes)
    })


@sync_bp.get("/pull")
def pull_changes():
    since = request.args.get("since")

    return jsonify({
        "server_time": None,
        "since": since,
        "changes": []
    })