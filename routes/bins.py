# routes/bins.py

from flask import Blueprint, jsonify

bins_bp = Blueprint("bins", __name__)

# Temporary bin data
# Later this can come from database

BINS = [
    {
        "id": 1,
        "name": "Main Gate Recycling Point",
        "lat": 21.1627,
        "lng": 81.7371,
        "type": "plastic",
        "accepts": ["Plastic", "Paper", "Metal"]
    },
    {
        "id": 2,
        "name": "Academic Block A — Organic Bin",
        "lat": 21.1634,
        "lng": 81.7382,
        "type": "organic",
        "accepts": ["Organic", "Food Waste"]
    },
    {
        "id": 3,
        "name": "Library E-Waste Drop",
        "lat": 21.1619,
        "lng": 81.7390,
        "type": "ewaste",
        "accepts": ["E-Waste", "Batteries", "Cables"]
    },
    {
        "id": 4,
        "name": "Canteen Waste Station",
        "lat": 21.1641,
        "lng": 81.7360,
        "type": "organic",
        "accepts": ["Organic", "Food Waste", "Plastic"]
    },
    {
        "id": 5,
        "name": "Hostel Block — General Bin",
        "lat": 21.1614,
        "lng": 81.7375,
        "type": "general",
        "accepts": ["General Waste"]
    }
]


@bins_bp.route("/api/bins", methods=["GET"])
def get_bins():
    """
    Return all campus bins
    """

    return jsonify({
        "status": "success",
        "bins": BINS
    })