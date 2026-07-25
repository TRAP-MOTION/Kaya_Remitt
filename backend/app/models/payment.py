from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_payment_id():
    return f"PAY{uuid.uuid4().hex[:6].upper()}"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.String(36), primary_key=True, default=generate_payment_id)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False, index=True
    )
    merchant_id = db.Column(
        db.String(36), db.ForeignKey("merchants.id"), nullable=False, index=True
    )
    service_id = db.Column(
        db.String(36), db.ForeignKey("services.id"), nullable=False, index=True
    )
    beneficiary_name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="COMPLETED")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])
    merchant = db.relationship("Merchant", foreign_keys=[merchant_id])
    service = db.relationship("Service", foreign_keys=[service_id])

    def to_dict(self):
        return {
            "payment_id": self.id,
            "merchant": self.merchant.business_name if self.merchant else None,
            "service": self.service.name if self.service else None,
            "beneficiary_name": self.beneficiary_name,
            "amount": round(float(self.amount), 2),
            "status": self.status,
        }
