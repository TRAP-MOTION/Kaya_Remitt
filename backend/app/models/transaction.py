from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    payment_id = db.Column(
        db.String(36),
        db.ForeignKey("payments.payment_id"),
        nullable=False,
        index=True,
    )
    action = db.Column(db.String(100), nullable=False)
    performed_by = db.Column(
        db.String(36), db.ForeignKey("users.user_id"), nullable=False, index=True
    )
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    payment = db.relationship("Payment", back_populates="transactions")
    performer = db.relationship("User", foreign_keys=[performed_by])

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "payment_id": self.payment_id,
            "action": self.action,
            "performed_by": self.performed_by,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
