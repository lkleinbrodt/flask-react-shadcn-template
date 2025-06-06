from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import relationship

from backend.extensions import db


class TransactionType(str, Enum):
    """Types of balance transactions"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"


class TransactionStatus(str, Enum):
    """Status of balance transactions"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class UserBalance(db.Model):
    """Tracks user balance across all applications"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True
    )
    balance = db.Column(
        db.Numeric(10, 2), nullable=False, default=5.00
    )  # Start with $5 free credit
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # Relationship with User model
    user = relationship("User", backref="balance", uselist=False)

    def has_sufficient_balance(self, amount):
        """Check if user has sufficient balance for a transaction"""
        return self.balance >= Decimal(str(amount))

    def debit(self, amount):
        """Remove money from balance"""
        if not self.has_sufficient_balance(amount):
            raise ValueError("Insufficient balance")
        self.balance -= Decimal(str(amount))

    def credit(self, amount):
        """Add money to balance"""
        self.balance += Decimal(str(amount))

    def to_dict(self):
        return {
            "balance": float(self.balance),
            "updated_at": self.updated_at.isoformat(),
        }


class Transaction(db.Model):
    """Records all balance transactions across applications"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    balance_id = db.Column(db.Integer, db.ForeignKey("user_balance.id"), nullable=False)
    application = db.Column(
        db.String(50), nullable=False
    )  # e.g., 'speech', 'autodraft'
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    operation = db.Column(db.String(50), nullable=True)  # App-specific operation type
    status = db.Column(
        db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING
    )
    reference_id = db.Column(
        db.Integer, nullable=True
    )  # For linking to app-specific resources
    transaction_metadata = db.Column(
        db.JSON, nullable=True
    )  # For app-specific additional data
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    user = relationship("User", backref="transactions")
    balance = relationship("UserBalance", backref="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "application": self.application,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type.value,
            "operation": self.operation,
            "status": self.status.value,
            "reference_id": self.reference_id,
            "transaction_metadata": self.transaction_metadata,
            "created_at": self.created_at.isoformat(),
        }
