# routes/dispose.py

from flask import Blueprint, request, jsonify
from datetime import datetime

from services.database_service import (
    update_user_points,
    log_waste_scan,
    get_waste_type_id
)

dispose_bp = Blueprint("dispose", __name__)


@dispose_bp.route("/api/dispose", methods=["POST"])
def confirm_disposal():
    """
    Confirm that the waste was disposed properly
    and award eco-points to the user
    """

    try:

        data = request.json

        user_id = data.get("user_id")
        waste_type = data.get("waste_type")
        eco_points = data.get("eco_points")
        lat = data.get("lat")
        lon = data.get("lon")

        if not user_id or not waste_type:
            return jsonify({
                "status": "error",
                "message": "Missing required data"
            }), 400

        # Get waste type id from database
        waste_type_id = get_waste_type_id(waste_type)

        # Log waste scan
        log_waste_scan(
            user_id=user_id,
            waste_type_id=waste_type_id,
            eco_points=eco_points,
            latitude=lat,
            longitude=lon
        )

        # Update user eco points
        update_user_points(user_id, eco_points)

        return jsonify({
            "status": "success",
            "message": "Waste disposal confirmed",
            "points_awarded": eco_points
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500