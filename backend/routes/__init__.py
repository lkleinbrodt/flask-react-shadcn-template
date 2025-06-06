from flask import Blueprint, jsonify

from backend.routes.auth import auth_bp
from backend.routes.billing import billing_bp

base_bp = Blueprint("base", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(billing_bp)


@base_bp.route("/")
def index():
    """Base root, returns basic status."""
    return jsonify(
        {"status": "healthy", "message": "This page intentionally left blank."}
    )


@api_bp.route("/")
def index():
    """API root, returns basic status."""
    return jsonify({"status": "healthy", "message": "Welcome to the API!"})
