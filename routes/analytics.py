# routes/analytics.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from services.database_service import (
    get_waste_heatmap_data,
    get_waste_type_stats,
    get_daily_waste_trend
)

analytics_bp = Blueprint("analytics", __name__)


# --------------------------------
# WASTE HEATMAP DATA
# --------------------------------
@analytics_bp.route("/analytics/heatmap", methods=["GET"])
@jwt_required()
def waste_heatmap():
    """
    Return coordinates and waste counts for heatmap
    """

    data = get_waste_heatmap_data()

    return jsonify({
        "status": "success",
        "data": data
    })


# --------------------------------
# WASTE TYPE DISTRIBUTION
# --------------------------------
@analytics_bp.route("/analytics/waste-types", methods=["GET"])
@jwt_required()
def waste_types():

    data = get_waste_type_stats()

    return jsonify({
        "status": "success",
        "data": data
    })


# --------------------------------
# DAILY WASTE TREND
# --------------------------------
@analytics_bp.route("/analytics/daily-trends", methods=["GET"])
@jwt_required()
def daily_trends():

    data = get_daily_waste_trend()

    return jsonify({
        "status": "success",
        "data": data
    })