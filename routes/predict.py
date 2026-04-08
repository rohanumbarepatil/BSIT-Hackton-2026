# routes/predict.py

from flask import Blueprint, request, jsonify

# Model
from models.waste_model import classifier

# Utils
from utils.image_processing import preprocess_image

# Services
from services.eco_points import calculate_points
from services.image_similarity import generate_image_hash, is_duplicate, store_hash

# Config
from config import CONFIDENCE_THRESHOLD

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    Waste classification endpoint
    """

    try:

        # -----------------------------
        # 1️⃣ Check if image uploaded
        # -----------------------------
        if "image" not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image uploaded"
            }), 400

        file = request.files["image"]

        # -----------------------------
        # 2️⃣ Duplicate detection
        # -----------------------------
        image_hash = generate_image_hash(file)

        if is_duplicate(image_hash):
            return jsonify({
                "status": "rejected",
                "message": "Duplicate waste scan detected"
            })

        store_hash(image_hash)

        file.seek(0)

        # -----------------------------
        # 3️⃣ Preprocess image
        # -----------------------------
        image = preprocess_image(file)

        # -----------------------------
        # 4️⃣ Run AI prediction
        # -----------------------------
        waste_type, confidence = classifier.predict(image)

        # -----------------------------
        # 5️⃣ Confidence validation
        # -----------------------------
        if confidence < CONFIDENCE_THRESHOLD:
            return jsonify({
                "status": "uncertain",
                "message": "Unable to confidently classify waste",
                "confidence": confidence
            })

        # -----------------------------
        # 6️⃣ Calculate eco points
        # -----------------------------
        eco_points = calculate_points(waste_type)

        # -----------------------------
        # 7️⃣ Return prediction result
        # -----------------------------
        return jsonify({
            "status": "success",
            "data": {
                "waste_type": waste_type,
                "confidence": confidence,
                "eco_points": eco_points
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500