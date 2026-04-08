# routes/users.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Database services
from services.database_service import (
    get_user_dashboard,
    get_user_badges,
    get_all_users_from_db
)

users_bp = Blueprint("users", __name__)


# --------------------------------
# USER DASHBOARD
# --------------------------------
@users_bp.route("/users/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    """
    Return dashboard data for logged-in user
    """

    user_id = get_jwt_identity()

    dashboard_data = get_user_dashboard(user_id)
    badges = get_user_badges(user_id)

    return jsonify({
        "status": "success",
        "data": {
            "eco_points": dashboard_data["points"],
            "total_scans": dashboard_data["scans"],
            "badges": badges,
            "waste_distribution": dashboard_data["waste_distribution"]
        }
    })


# --------------------------------
# GET USER PROFILE
# --------------------------------
@users_bp.route("/users/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """
    Return basic profile info for logged-in user
    """

    user_id = get_jwt_identity()

    dashboard_data = get_user_dashboard(user_id)

    return jsonify({
        "status": "success",
        "data": {
            "user_id": user_id,
            "eco_points": dashboard_data["points"],
            "total_scans": dashboard_data["scans"]
        }
    })


# --------------------------------
# GET ALL USERS (LEADERBOARD USE)
# --------------------------------
@users_bp.route("/users", methods=["GET"])
def get_all_users():
    """
    Return all users from database
    """

    users = get_all_users_from_db()

    return jsonify({
        "status": "success",
        "data": users
    })
    
@users_bp.route("/api/user/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Return currently logged in user profile
    """

    try:

        # Get user identity from JWT token
        user_id = get_jwt_identity()

        dashboard_data = get_user_dashboard(user_id)

        badges = get_user_badges(user_id)

        return jsonify({
            "status": "success",
            "user": {
                "username": dashboard_data["username"],
                "points": dashboard_data["eco_points"],
                "scan_count": dashboard_data["waste_scanned"],
                "level": dashboard_data["level"],
                "rank": dashboard_data["rank"]
            },
            "badges": badges
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500