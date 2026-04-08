from flask import Blueprint, jsonify
from services.database_service import get_user_profile

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/api/user/me", methods=["GET"])
def me():

    # temporary user for demo/testing
    user_id = 1

    data = get_user_profile(user_id)

    return jsonify({
        "status": "success",
        "user": data
    })