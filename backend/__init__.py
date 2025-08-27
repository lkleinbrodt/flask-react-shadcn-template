import os

from flask import Flask

from backend.config import Config
from backend.extensions import cors, db, jwt, limiter, mail, migrate, talisman


def create_app(config_class: Config):

    app = Flask(
        __name__,
    )

    app.config.from_object(config_class)
    jwt.init_app(app)
    db.init_app(app)
    migrations_dir = os.path.join(app.root_path, "migrations")
    migrate.init_app(app, db, directory=migrations_dir)
    mail.init_app(app)

    # Initialize CORS with configurable origins and credentials support
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS", []),
        supports_credentials=True,
    )

    # Initialize security extensions
    limiter.init_app(app)
    talisman.init_app(
        app,
        force_https=os.getenv("FLASK_ENV") == "production",
        content_security_policy=None,  # Start with a permissive CSP
    )

    # Import blueprints
    from backend.routes import api_bp, base_bp

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(base_bp)
    return app
