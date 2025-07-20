import os
from datetime import datetime, timedelta

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import bcrypt

from backend.extensions import db, jwt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), nullable=True)
    apple_id = db.Column(db.String(255), nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)

    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    email_verified = db.Column("emailVerified", db.DateTime, nullable=True)
    password_hash = db.Column(
        db.String(128), nullable=True
    )  # Nullable to allow OAuth-only users

    created_at = db.Column(
        "createdAt", db.DateTime, nullable=False, default=db.func.now()
    )
    updated_at = db.Column(
        "updatedAt",
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        onupdate=db.func.now(),
    )

    group = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.verify(password, self.password_hash)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.id, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, salt="password-reset-salt", max_age=1800)
        except Exception:
            return None
        return User.query.get(user_id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "image": self.image,
        }

    def __repr__(self):
        return f"<User {self.id}>"

    def __str__(self) -> str:
        return f"<User {self.id}>"


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    # decode the jwt_data
    identity = jwt_data["sub"]
    # Convert string identity back to integer for database lookup
    return User.query.filter_by(id=int(identity)).one_or_none()


# Tell Flask-JWT-Extended to check this table for every protected request
@jwt.token_in_blocklist_loader
def check_if_token_revoked(_jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).one_or_none()
    return token is not None
