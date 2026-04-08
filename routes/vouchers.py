from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import string
from services.database_service import redeem_voucher, get_user_points

vouchers_bp = Blueprint("vouchers", __name__)

def generate_code():
    return "WW-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))


@vouchers_bp.route("/api/redeem", methods=["POST"])
@jwt_required()
def redeem():

    user_id = get_jwt_identity()
    reward = request.json.get("reward")

    points_required = 500

    points = get_user_points(user_id)

    if points < points_required:
        return jsonify({"error":"Not enough points"}), 400

    code = generate_code()

    redeem_voucher(user_id, reward, points_required, code)

    return jsonify({
        "status":"success",
        "voucher_code":code
    })
@vouchers_bp.route("/api/vouchers", methods=["GET"])
@jwt_required()
def user_vouchers():

    user_id = get_jwt_identity()

    vouchers = get_user_vouchers(user_id)

    return jsonify(vouchers)