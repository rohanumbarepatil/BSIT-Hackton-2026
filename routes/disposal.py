from flask import Blueprint, request, jsonify
from services.bin_locator import validate_user_location
from services.database_service import log_disposal

dispose_bp = Blueprint("dispose", __name__)

@dispose_bp.route("/api/dispose", methods=["POST"])
def dispose():

    try:

        data = request.json

        user_id = data.get("user_id")   # frontend sends this
        waste_type = data.get("waste_type")
        eco_points = data.get("eco_points")
        lat = data.get("lat")
        lon = data.get("lon")

        # check bin proximity
        is_valid, bin_name = validate_user_location(lat, lon)

        if not is_valid:
            return jsonify({
                "status": "rejected",
                "message": "You must be within 5 meters of a waste bin to earn points."
            })

        # store disposal
        log_disposal(user_id, waste_type, eco_points, lat, lon)

        return jsonify({
            "status": "success",
            "points_awarded": eco_points,
            "bin": bin_name
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500