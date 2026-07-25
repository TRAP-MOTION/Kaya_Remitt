from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class Service(db.Model):
    __tablename__ = "services"

    service_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    merchant_id = db.Column(
        db.String(36),
        db.ForeignKey("merchants.merchant_id"),
        nullable=False,
        index=True,
    )
    service_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    availability = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    merchant = db.relationship("Merchant", back_populates="services")
    payments = db.relationship("Payment", back_populates="service", lazy="dynamic")

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "name": self.service_name,
            "amount": round(float(self.price), 2),
        }
