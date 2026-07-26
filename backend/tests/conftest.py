"""Global pytest fixtures for KayaRemitt backend test suite."""
import pytest
from backend.app import create_app
from backend.app.extensions import db as _db
from backend.app.models.users import User
from backend.app.models.merchant_category import MerchantCategory
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service
from backend.app.models.payment import Payment
from backend.app.models.voucher import Voucher
from backend.app.models.support_ticket import SupportTicket
from backend.app.utils.auth import generate_token


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing with in-memory SQLite database."""
    _app = create_app("testing")
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-secret-key",
        "PAYCHANGU_SECRET_KEY": "test-paychangu-secret",
        "PAYCHANGU_CALLBACK_URL": "https://example.com/callback",
        "PAYCHANGU_RETURN_URL": "https://example.com/return",
        "PAYCHANGU_CURRENCY": "MWK",
    })

    with _app.app_context():
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture(scope="function")
def db_session(app):
    """Provides a fresh database session for a test function."""
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db_session):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def diaspora_user(db_session):
    """Fixture to create a standard diaspora user."""
    user = User(
        full_name="John Banda",
        email="john.banda@example.com",
        role="diaspora",
        country="United Kingdom",
    )
    user.set_password("Password123!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def diaspora_token(diaspora_user):
    """Fixture providing JWT token for diaspora user."""
    return generate_token(diaspora_user.user_id)


@pytest.fixture
def diaspora_headers(diaspora_token):
    """Fixture providing Authorization headers for diaspora user."""
    return {"Authorization": f"Bearer {diaspora_token}"}


@pytest.fixture
def merchant_user(db_session):
    """Fixture to create a user with 'merchant' role."""
    user = User(
        full_name="Chipiku Merchant",
        email="merchant@chipiku.mw",
        role="merchant",
        country="Malawi",
    )
    user.set_password("MerchantPass123!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def merchant_token(merchant_user):
    """Fixture providing JWT token for merchant user."""
    return generate_token(merchant_user.user_id)


@pytest.fixture
def merchant_headers(merchant_token):
    """Fixture providing Authorization headers for merchant user."""
    return {"Authorization": f"Bearer {merchant_token}"}


@pytest.fixture
def admin_user(db_session):
    """Fixture to create an admin user."""
    user = User(
        full_name="Admin User",
        email="admin@kayaremit.test",
        role="admin",
        country="Malawi",
        account_status="Active",
    )
    user.set_password("AdminPass123!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_headers(admin_user):
    """Fixture providing Authorization headers for admin user."""
    return {"Authorization": f"Bearer {generate_token(admin_user.user_id)}"}


@pytest.fixture
def sample_support_ticket(db_session, diaspora_user):
    """Fixture to create an open support ticket."""
    ticket = SupportTicket(
        user_id=diaspora_user.user_id,
        category="Complaint",
        subject="Merchant refused voucher",
        description="The merchant declined to honor a valid voucher code.",
        status="Open",
    )
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def sample_merchant(db_session, merchant_user):
    """Fixture to seed a verified Merchant, category, and service."""
    category = MerchantCategory(category_name="Groceries")
    db_session.add(category)
    db_session.flush()

    merchant = Merchant(
        category_id=category.category_id,
        business_name="Chipiku Plus",
        email=merchant_user.email,
        phone="+265991234567",
        city="Lilongwe",
        district="Lilongwe",
        verification_status="Verified",
    )
    db_session.add(merchant)
    db_session.flush()

    service = Service(
        merchant_id=merchant.merchant_id,
        service_name="Grocery Package",
        description="Standard food and essential bundle",
        price=50000.00,
        availability=True,
    )
    db_session.add(service)
    db_session.commit()

    return {
        "category": category,
        "merchant": merchant,
        "service": service,
    }


@pytest.fixture
def unverified_merchant(db_session):
    """Fixture to seed an unverified Merchant and service."""
    category = MerchantCategory(category_name="Electronics")
    db_session.add(category)
    db_session.flush()

    merchant = Merchant(
        category_id=category.category_id,
        business_name="Pending Tech Store",
        email="pending@tech.mw",
        phone="+265888123456",
        city="Blantyre",
        district="Blantyre",
        verification_status="Pending",
    )
    db_session.add(merchant)
    db_session.flush()

    service = Service(
        merchant_id=merchant.merchant_id,
        service_name="Smartphone",
        price=150000.00,
        availability=True,
    )
    db_session.add(service)
    db_session.commit()

    return {
        "merchant": merchant,
        "service": service,
    }


@pytest.fixture
def sample_payment(db_session, diaspora_user, sample_merchant):
    """Fixture to create a completed payment."""
    merchant = sample_merchant["merchant"]
    service = sample_merchant["service"]

    payment = Payment(
        user_id=diaspora_user.user_id,
        merchant_id=merchant.merchant_id,
        service_id=service.service_id,
        beneficiary_name="Mary Banda",
        amount=50000.00,
        payment_status="COMPLETED",
    )
    db_session.add(payment)
    db_session.commit()
    return payment


@pytest.fixture
def sample_voucher(db_session, sample_payment):
    """Fixture to create an active voucher linked to sample_payment."""
    voucher = Voucher(
        payment_id=sample_payment.payment_id,
        status="Active",
    )
    db_session.add(voucher)
    db_session.commit()
    return voucher
