import pytest
from decimal import Decimal

from backend.models.user import User
from backend.models.billing import UserBalance, Transaction, TransactionType, TransactionStatus
from backend.extensions import db


class TestUserModel:
    """Test the User model."""
    
    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                google_id="google_123",
                name="John Doe",
                email="john@example.com",
                image="https://example.com/avatar.jpg"
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.google_id == "google_123"
            assert user.name == "John Doe"
            assert user.email == "john@example.com"
            assert user.image == "https://example.com/avatar.jpg"
            assert user.created_at is not None
            assert user.updated_at is not None
            
    def test_user_string_representation(self, app):
        """Test User model string representation."""
        with app.app_context():
            user = User(name="Test User", email="test@example.com")
            db.session.add(user)
            db.session.commit()
            
            assert str(user) == f"<User {user.id}>"
            assert repr(user) == f"<User {user.id}>"


class TestUserBalanceModel:
    """Test the UserBalance model."""
    
    def test_user_balance_creation(self, app, test_user):
        """Test creating a user balance."""
        with app.app_context():
            balance = UserBalance(user_id=test_user.id)
            db.session.add(balance)
            db.session.commit()
            
            assert balance.user_id == test_user.id
            assert balance.balance == Decimal("5.00")  # Default balance
            assert balance.created_at is not None
            assert balance.updated_at is not None
            
    def test_user_balance_credit(self, app, test_user):
        """Test crediting user balance."""
        with app.app_context():
            balance = UserBalance(user_id=test_user.id)
            db.session.add(balance)
            db.session.commit()
            
            initial_balance = balance.balance
            credit_amount = Decimal("10.00")
            
            balance.credit(credit_amount)
            db.session.commit()
            
            assert balance.balance == initial_balance + credit_amount
            
    def test_user_balance_debit_sufficient_funds(self, app, test_user):
        """Test debiting user balance with sufficient funds."""
        with app.app_context():
            balance = UserBalance(user_id=test_user.id)
            db.session.add(balance)
            db.session.commit()
            
            initial_balance = balance.balance
            debit_amount = Decimal("2.00")  # Less than default $5.00
            
            success = balance.debit(debit_amount)
            db.session.commit()
            
            assert success is True
            assert balance.balance == initial_balance - debit_amount
            
    def test_user_balance_debit_insufficient_funds(self, app, test_user):
        """Test debiting user balance with insufficient funds."""
        with app.app_context():
            balance = UserBalance(user_id=test_user.id)
            db.session.add(balance)
            db.session.commit()
            
            initial_balance = balance.balance
            debit_amount = Decimal("10.00")  # More than default $5.00
            
            success = balance.debit(debit_amount)
            db.session.commit()
            
            assert success is False
            assert balance.balance == initial_balance  # Should remain unchanged
            
    def test_user_balance_to_dict(self, app, test_user):
        """Test UserBalance to_dict method."""
        with app.app_context():
            balance = UserBalance(user_id=test_user.id)
            db.session.add(balance)
            db.session.commit()
            
            balance_dict = balance.to_dict()
            
            assert "user_id" in balance_dict
            assert "balance" in balance_dict
            assert "created_at" in balance_dict
            assert "updated_at" in balance_dict
            assert balance_dict["user_id"] == test_user.id
            assert balance_dict["balance"] == float(balance.balance)


class TestTransactionModel:
    """Test the Transaction model."""
    
    def test_transaction_creation(self, app, test_user):
        """Test creating a transaction."""
        with app.app_context():
            transaction = Transaction(
                user_id=test_user.id,
                amount=Decimal("10.00"),
                transaction_type=TransactionType.CREDIT,
                status=TransactionStatus.COMPLETED,
                description="Test credit"
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.user_id == test_user.id
            assert transaction.amount == Decimal("10.00")
            assert transaction.transaction_type == TransactionType.CREDIT
            assert transaction.status == TransactionStatus.COMPLETED
            assert transaction.description == "Test credit"
            assert transaction.created_at is not None
            assert transaction.updated_at is not None
            
    def test_transaction_to_dict(self, app, test_user):
        """Test Transaction to_dict method."""
        with app.app_context():
            transaction = Transaction(
                user_id=test_user.id,
                amount=Decimal("5.00"),
                transaction_type=TransactionType.DEBIT,
                status=TransactionStatus.PENDING,
                description="Test debit"
            )
            db.session.add(transaction)
            db.session.commit()
            
            transaction_dict = transaction.to_dict()
            
            assert "id" in transaction_dict
            assert "user_id" in transaction_dict
            assert "amount" in transaction_dict
            assert "transaction_type" in transaction_dict
            assert "status" in transaction_dict
            assert "description" in transaction_dict
            assert "created_at" in transaction_dict
            assert "updated_at" in transaction_dict
            
            assert transaction_dict["user_id"] == test_user.id
            assert transaction_dict["amount"] == float(transaction.amount)
            assert transaction_dict["transaction_type"] == TransactionType.DEBIT.value
            assert transaction_dict["status"] == TransactionStatus.PENDING.value