# app.py

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Config
from config import DEBUG, APP_NAME, JWT_SECRET_KEY

# Routes
from routes.predict import predict_bp
from routes.users import users_bp
from routes.auth import auth_bp
from routes.leaderboard import leaderboard_bp
from routes.analytics import analytics_bp
from routes.rewards import rewards_bp
from routes.vouchers import vouchers_bp
from routes.games import games_bp
from routes.bins import bins_bp
from routes.disposal import dispose_bp
from routes.user_profile import profile_bp


def create_app():
    """
    WasteSense AI Application Factory
    """

    app = Flask(APP_NAME)

    # -----------------------------
    # Core Configuration
    # -----------------------------
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False

    # -----------------------------
    # Enable CORS (frontend 5500)
    # -----------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True
    )

    # -----------------------------
    # Initialize JWT
    # -----------------------------
    JWTManager(app)

    # -----------------------------
    # Register API Blueprints
    # -----------------------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(predict_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(vouchers_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(bins_bp)
    app.register_blueprint(dispose_bp)
    app.register_blueprint(profile_bp)

    # -----------------------------
    # Root Endpoint
    # -----------------------------
    @app.route("/")
    def home():
        return jsonify({
            "message": "Welcome to WasteSense AI API",
            "status": "running"
        })

    # -----------------------------
    # Health Check
    # -----------------------------
    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "WasteSense Backend"
        })

    return app


# -----------------------------
# Run Application
# -----------------------------
app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=DEBUG
    )