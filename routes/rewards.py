# routes/rewards.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import string

from services.database_service import (
    update_user_points,
    get_user_dashboard
)

rewards_bp = Blueprint("rewards", __name__)

# Temporary storage
# Later move to database
user_vouchers = []

# Reward catalog
REWARDS = {
    "swiggy": 200,
    "amazon": 500,
    "canteen": 100
}


def generate_voucher_code():
    prefix = "WW"
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return f"{prefix}-{code}"


@rewards_bp.route("/api/redeem", methods=["POST"])
@jwt_required()
def redeem_reward():

    try:

        user_id = get_jwt_identity()
        data = request.json

        reward_type = data.get("reward")

        if reward_type not in REWARDS:
            return jsonify({
                "status": "error",
                "message": "Invalid reward"
            })

        cost = REWARDS[reward_type]

        user = get_user_dashboard(user_id)
        points = user["eco_points"]

        if points < cost:
            return jsonify({
                "status": "error",
                "message": "Not enough eco points"
            })

        # Deduct points
        update_user_points(user_id, -cost)

        # Generate voucher
        code = generate_voucher_code()

        voucher = {
            "user_id": user_id,
            "reward": reward_type,
            "code": code
        }

        user_vouchers.append(voucher)

        return jsonify({
            "status": "success",
            "voucher_code": code,
            "reward": reward_type
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })
        
@rewards_bp.route("/api/vouchers", methods=["GET"])
@jwt_required()
def get_vouchers():

    user_id = get_jwt_identity()

    vouchers = [v for v in user_vouchers if v["user_id"] == user_id]

    return jsonify({
        "status": "success",
        "vouchers": vouchers
    })