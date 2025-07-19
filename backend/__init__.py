import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from backend.config import Config
from backend.extensions import cors, db, jwt, migrate


def create_app(config_class: Config):

    app = Flask(
        __name__,
    )

    app.config.from_object(config_class)
    jwt.init_app(app)
    db.init_app(app)
    migrations_dir = os.path.join(app.root_path, "migrations")
    migrate.init_app(app, db, directory=migrations_dir)
    cors.init_app(app)

    # Register centralized error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all unhandled exceptions with consistent JSON response."""
        # Pass through HTTP exceptions
        if isinstance(e, HTTPException):
            return jsonify(error=str(e.description)), e.code
        # Handle non-HTTP exceptions
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify(error="An unexpected error occurred. See server logs for details."), 500

    @app.errorhandler(404)
    def resource_not_found(e):
        """Handle 404 errors with consistent JSON response."""
        return jsonify(error="Resource not found"), 404

    @app.errorhandler(400)
    def bad_request(e):
        """Handle 400 errors with consistent JSON response."""
        return jsonify(error=str(e.description)), 400

    # Import blueprints
    from backend.routes import api_bp, base_bp

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(base_bp)
    return app
