# routes/leaderboard.py

from flask import Blueprint, jsonify
from services.database_service import get_leaderboard

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """
    Return top users ranked by eco points
    """

    try:

        leaderboard_data = get_leaderboard()

        return jsonify({
            "status": "success",
            "leaderboard": leaderboard_data
        }), 200

    except Exception as e:

        print("Leaderboard error:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500