from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


def generate_transaction_reference():
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


# Payment status lifecycle:
# AwaitingAcceptance → merchant notified; awaiting accept/deny
# Accepted           → merchant approved; user can start checkout
# Denied             → merchant rejected; checkout blocked
# Pending            → checkout initiated; awaiting PayChangu payment
# COMPLETED          → PayChangu verified; voucher can be issued


class Payment(db.Model):
    __tablename__ = "payments"

    payment_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.user_id"), nullable=False, index=True
    )
    merchant_id = db.Column(
        db.String(36),
        db.ForeignKey("merchants.merchant_id"),
        nullable=False,
        index=True,
    )
    service_id = db.Column(
        db.String(36),
        db.ForeignKey("services.service_id"),
        nullable=False,
        index=True,
    )
    beneficiary_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="AwaitingAcceptance")
    transaction_reference = db.Column(
        db.String(100), unique=True, nullable=False, default=generate_transaction_reference
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", back_populates="payments")
    merchant = db.relationship("Merchant", back_populates="payments")
    service = db.relationship("Service", back_populates="payments")
    voucher = db.relationship(
        "Voucher", back_populates="payment", uselist=False, cascade="all, delete-orphan"
    )
    transactions = db.relationship(
        "Transaction", back_populates="payment", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "merchant": self.merchant.business_name if self.merchant else None,
            "service": self.service.service_name if self.service else None,
            "beneficiary_name": self.beneficiary_name,
            "amount": round(float(self.amount), 2),
            "status": self.payment_status,
        }
