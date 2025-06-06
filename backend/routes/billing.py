import json
from decimal import Decimal

import stripe
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import create_logger, db
from backend.models.billing import (
    Transaction,
    TransactionStatus,
    TransactionType,
    UserBalance,
)
from backend.models.user import User

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")
logger = create_logger(__name__, level="DEBUG")


@billing_bp.route("/balance", methods=["GET"])
@jwt_required()
def get_balance():
    """Get current user's balance"""
    user_id = get_jwt_identity()
    balance = UserBalance.query.filter_by(user_id=user_id).first()

    if not balance:
        # Create initial balance with $5.00 for new users
        balance = UserBalance(user_id=user_id)
        db.session.add(balance)
        db.session.commit()

    return jsonify(balance.to_dict())


@billing_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    user_id = get_jwt_identity()
    application = request.args.get("application")  # Optional filter by application

    query = Transaction.query.filter_by(user_id=user_id)
    if application:
        query = query.filter_by(application=application)

    transactions = query.order_by(Transaction.created_at.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


@billing_bp.route("/balance/add", methods=["POST"])
@jwt_required()
def add_funds():
    """Add funds to user's balance"""
    user_id = get_jwt_identity()
    data = request.get_json()
    amount = Decimal(str(data.get("amount", 0)))

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    balance = UserBalance.query.filter_by(user_id=user_id).first()
    if not balance:
        balance = UserBalance(user_id=user_id)
        db.session.add(balance)

    # Create transaction record
    transaction = Transaction(
        user_id=user_id,
        balance_id=balance.id,
        application=data.get(
            "application", "platform"
        ),  # Track which app initiated the purchase
        amount=amount,
        transaction_type=TransactionType.PURCHASE,
        status=TransactionStatus.COMPLETED,
        transaction_metadata=data.get("metadata"),
    )
    db.session.add(transaction)

    # Update balance
    balance.credit(amount)
    db.session.commit()

    return jsonify({"balance": balance.to_dict(), "transaction": transaction.to_dict()})


@billing_bp.route("/stripe/publishable_key", methods=["GET"])
def fetch_stripe_publishable_key():
    return jsonify({"publishable_key": current_app.config["STRIPE_PUBLISHABLE_KEY"]})


@billing_bp.route("/create-payment-sheet", methods=["POST"])
@jwt_required()
def create_payment_sheet():
    """Create a Stripe PaymentSheet with customer and ephemeral key"""
    try:
        data = request.get_json()
        amount = data.get("amount")

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Amount should be in cents for Stripe
        stripe_amount = int(float(amount) * 100)

        # Initialize Stripe with secret key
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

        # Get user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Get or create Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email, metadata={"user_id": user_id}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)

        # Create ephemeral key
        ephemeral_key = stripe.EphemeralKey.create(
            customer=customer.id,
            stripe_version=stripe.api_version,
        )

        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=stripe_amount,
            currency="usd",
            customer=customer.id,
            metadata={"user_id": user_id, "type": "add_funds"},
            automatic_payment_methods={"enabled": True},
        )

        return jsonify(
            {
                "paymentIntent": payment_intent.client_secret,
                "ephemeralKey": ephemeral_key.secret,
                "customer": customer.id,
                "publishableKey": current_app.config["STRIPE_PUBLISHABLE_KEY"],
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error creating payment sheet: {str(e)}")
        return jsonify({"error": "Failed to create payment sheet"}), 500


# use this command to test the webhook locally
# stripe listen --forward-to localhost:5002/api/billing/payment-webhook
@billing_bp.route("/payment-webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    logger.info("Received Stripe webhook event")
    event = None
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        # Initialize Stripe with secret key
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

        if endpoint_secret:
            # Only verify the event if there is an endpoint secret defined
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
                logger.debug(
                    f"Successfully verified Stripe webhook event: {event.type}"
                )
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"⚠️  Webhook signature verification failed: {str(e)}")
                return jsonify(success=False), 400
        else:
            # If no endpoint secret, parse the basic event
            try:
                event = json.loads(payload)
                logger.debug(f"Parsed basic Stripe event: {event.get('type')}")
            except json.decoder.JSONDecodeError as e:
                logger.error(f"⚠️  Webhook error while parsing basic request: {str(e)}")
                return jsonify(success=False), 400

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            current_app.logger.info(f"Payment for {payment_intent['amount']} succeeded")

            # Get user ID from metadata
            user_id = int(payment_intent["metadata"].get("user_id"))
            amount = float(payment_intent["amount"]) / 100  # Convert cents to dollars

            # Update user balance
            balance = UserBalance.query.filter_by(user_id=user_id).first()
            if not balance:
                balance = UserBalance(user_id=user_id)
                db.session.add(balance)

            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                balance_id=balance.id,
                application="platform",
                amount=amount,
                transaction_type=TransactionType.PURCHASE,
                status=TransactionStatus.COMPLETED,
                transaction_metadata={
                    "stripe_payment_intent": payment_intent["id"],
                    "stripe_payment_method": payment_intent.get("payment_method"),
                    "stripe_customer": payment_intent.get("customer"),
                },
            )
            db.session.add(transaction)

            # Update balance
            balance.credit(amount)
            db.session.commit()

        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            current_app.logger.error(f"❌ Payment failed: {payment_intent['id']}")

            # Get user ID from metadata
            user_id = int(payment_intent["metadata"].get("user_id"))
            amount = float(payment_intent["amount"]) / 100

            # Create failed transaction record
            transaction = Transaction(
                user_id=user_id,
                balance_id=UserBalance.query.filter_by(user_id=user_id).first().id,
                application="platform",
                amount=amount,
                transaction_type=TransactionType.PURCHASE,
                status=TransactionStatus.FAILED,
                transaction_metadata={
                    "stripe_payment_intent": payment_intent["id"],
                    "stripe_error": payment_intent.get("last_payment_error"),
                },
            )
            db.session.add(transaction)
            db.session.commit()

        elif event["type"] == "payment_intent.created":
            payment_intent = event["data"]["object"]
            current_app.logger.info(
                f"Payment intent {payment_intent['id']} created for amount {payment_intent['amount']}"
            )

        elif event["type"] == "charge.succeeded":
            charge = event["data"]["object"]
            current_app.logger.info(
                f"Charge {charge['id']} succeeded for amount {charge['amount']}"
            )
            # The payment_intent.succeeded event is already handling the balance update,
            # so we just log this event

        elif event["type"] == "charge.updated":
            charge = event["data"]["object"]
            current_app.logger.info(
                f"Charge {charge['id']} was updated. New status: {charge['status']}"
            )

        elif event["type"] == "payment_method.attached":
            payment_method = event["data"]["object"]
            current_app.logger.info(f"Payment method {payment_method['id']} attached")

        else:
            # Unexpected event type
            current_app.logger.warning(f"Unhandled event type {event['type']}")

        return jsonify(success=True)

    except Exception as e:
        current_app.logger.error(f"Error handling webhook: {str(e)}")
        return jsonify(success=False), 500
