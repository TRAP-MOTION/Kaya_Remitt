from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


def generate_voucher_code():
    return f"KAYA-{uuid.uuid4().hex[:6].upper()}"


class Voucher(db.Model):
    __tablename__ = "vouchers"

    voucher_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    payment_id = db.Column(
        db.String(36),
        db.ForeignKey("payments.payment_id"),
        nullable=False,
        unique=True,
        index=True,
    )
    voucher_code = db.Column(
        db.String(100), unique=True, nullable=False, default=generate_voucher_code
    )
    status = db.Column(db.String(20), nullable=False, default="Active")
    issued_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    redeemed_at = db.Column(db.DateTime, nullable=True)

    payment = db.relationship("Payment", back_populates="voucher")

    def to_dict(self):
        payment = self.payment
        merchant_name = None
        amount = None
        if payment:
            amount = round(float(payment.amount), 2)
            if payment.merchant:
                merchant_name = payment.merchant.business_name
        return {
            "voucher_id": self.voucher_code,
            "status": self.status.upper() if self.status else None,
            "merchant": merchant_name,
            "amount": amount,
        }
