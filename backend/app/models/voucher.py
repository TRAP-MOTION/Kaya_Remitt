from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_voucher_id():
    # Produces IDs like "KAYA-A1B2C3" matching the spec example format
    return f"KAYA-{uuid.uuid4().hex[:6].upper()}"


class Voucher(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.String(36), primary_key=True, default=generate_voucher_id)
    payment_id = db.Column(
        db.String(36), db.ForeignKey("payments.id"), nullable=False, unique=True, index=True
    )
    merchant_id = db.Column(
        db.String(36), db.ForeignKey("merchants.id"), nullable=False, index=True
    )
    amount = db.Column(db.Float, nullable=False)
    # Possible statuses: ACTIVE, VALID (alias for ACTIVE on verify), REDEEMED
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    payment = db.relationship("Payment", foreign_keys=[payment_id])
    merchant = db.relationship("Merchant", foreign_keys=[merchant_id])

    def to_dict(self):
        return {
            "voucher_id": self.id,
            "status": self.status,
            "merchant": self.merchant.business_name if self.merchant else None,
            "amount": round(float(self.amount), 2),
        }
