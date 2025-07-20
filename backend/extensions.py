import logging

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate(render_as_batch=True)
cors = CORS(supports_credentials=True)
talisman = Talisman()
limiter = Limiter(get_remote_address)
mail = Mail()


def create_logger(name, level="INFO"):
    # Create a logger instance
    logger = logging.getLogger(name)

    # Remove this comment to enable the level setting
    logger.setLevel(level)

    # Check if handler already exists to prevent duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        import sys

        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = create_logger("app")
