from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt

from services.database_service import create_user, get_user_by_email

auth_bp = Blueprint("auth", __name__)


# -------------------------
# USER SIGNUP
# -------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    user_id = create_user(name, email, hashed_password)

    return jsonify({
        "status": "success",
        "message": "User created successfully",
        "user_id": user_id
    })


# -------------------------
# USER LOGIN
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = get_user_by_email(email)

    if not user:
        return jsonify({"message": "User not found"}), 404

    stored_password = user["password"]

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8")
    ):
        return jsonify({"message": "Invalid password"}), 401

    token = create_access_token(identity=user["user_id"])

    return jsonify({
        "status": "success",
        "token": token,
        "user": {
            "id": user["user_id"],
            "name": user["name"],
            "email": user["email"]
        }
    })