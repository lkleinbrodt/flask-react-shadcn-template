import json
from decimal import Decimal

import stripe
from flask import Blueprint, current_app, jsonify, make_response, redirect, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from backend.extensions import db, limiter
from backend.models.user import TokenBlocklist, User
from backend.src.email_service import send_password_reset_email
from backend.src.OAuthSignIn import OAuthSignIn

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return jsonify(msg="Email and password required"), 400

    if User.query.filter_by(email=email).first():
        return jsonify(msg="Email already exists"), 409

    new_user = User(email=email, name=name if name else None)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(msg="User created successfully"), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(msg="Email and password required"), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify(msg="Bad email or password"), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify(user=user.to_dict())
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify(msg="logout successful")

    # Revoke access token
    access_jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=access_jti))
    db.session.commit()

    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/logout/refresh", methods=["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    response = jsonify(msg="refresh token revoked")

    # Revoke refresh token
    refresh_jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=refresh_jti))
    db.session.commit()

    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    # Revoke the old refresh token
    old_refresh_jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=old_refresh_jti))
    db.session.commit()

    # Create new tokens
    new_access_token = create_access_token(identity=identity)
    new_refresh_token = create_refresh_token(identity=identity)

    response = jsonify(msg="token refreshed")
    set_access_cookies(response, new_access_token)
    set_refresh_cookies(response, new_refresh_token)
    return response, 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    # current_user is populated by our user_lookup_loader
    if not current_user:
        return jsonify(msg="User not found"), 404
    return jsonify(user=current_user.to_dict()), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if user:
        send_password_reset_email(user)
    # Always return a success message to prevent email enumeration
    return (
        jsonify(
            message="If an account with that email exists, a password reset link has been sent."
        ),
        200,
    )


@auth_bp.route("/reset-password/<token>", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        return (
            jsonify(message="The password reset link is invalid or has expired."),
            400,
        )

    data = request.get_json()
    password = data.get("password")
    if not password:
        return jsonify(message="Password is required."), 400

    user.set_password(password)
    db.session.commit()
    return jsonify(message="Your password has been updated."), 200


# --- ADAPTED OAUTH FLOW ---
@auth_bp.route("/authorize/<provider>")
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth_bp.route("/callback/<provider>")
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email, picture = oauth.callback()

    if social_id is None:
        # Redirect to login with a generic failure message
        redirect_url = f"{current_app.config['FRONTEND_URL']}/login?error=oauth_failed"
        return redirect(redirect_url)

    user = User.query.filter_by(email=email).first()

    if user and not getattr(user, f"{provider}_id", None):
        # User exists but with a different login method (e.g., password).
        # Redirect to the login page with an informational message.
        redirect_url = f"{current_app.config['FRONTEND_URL']}/login?error=account_exists&email={email}"
        return redirect(redirect_url)

    if not user:
        # User does not exist, create a new one.
        user = User(email=email, name=name, image=picture)
        setattr(user, f"{provider}_id", social_id)
        db.session.add(user)
        db.session.commit()

    # User exists and is using the correct OAuth provider, or a new user was created.
    # Proceed with login.
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    redirect_url = f"{current_app.config['FRONTEND_URL']}/auth/callback"
    response = make_response(redirect(redirect_url))

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response
