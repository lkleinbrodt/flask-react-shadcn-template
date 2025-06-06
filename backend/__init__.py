from flask import Flask

from backend.config import Config
from backend.extensions import cors, db, jwt, migrate


def create_app(config_class: Config):

    app = Flask(
        __name__,
    )

    app.config.from_object(config_class)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Import blueprints
    from backend.routes import api_bp, base_bp

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(base_bp)
    return app
