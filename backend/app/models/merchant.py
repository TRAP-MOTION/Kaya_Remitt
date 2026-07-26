from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class Merchant(db.Model):
    __tablename__ = "merchants"

    merchant_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category_id = db.Column(
        db.String(36),
        db.ForeignKey("merchant_categories.category_id"),
        nullable=False,
        index=True,
    )
    business_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    verification_status = db.Column(db.String(20), nullable=False, default="Pending")
    logo = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = db.relationship("MerchantCategory", back_populates="merchants")
    services = db.relationship(
        "Service", back_populates="merchant", cascade="all, delete-orphan", lazy="dynamic"
    )
    payments = db.relationship("Payment", back_populates="merchant", lazy="dynamic")

    @property
    def verified(self):
        return self.verification_status.lower() == "verified"

    def _format_dt(self, value):
        if not value:
            return None
        formatted = value.isoformat()
        if formatted.endswith("+00:00"):
            return formatted[:-6] + "Z"
        if not formatted.endswith("Z"):
            return formatted + "Z"
        return formatted

    def to_dict(self, include_services=False):
        data = {
            "merchant_id": self.merchant_id,
            "business_name": self.business_name,
            "category": self.category.category_name if self.category else None,
            "location": self.city,
            "verified": self.verified,
        }
        if include_services:
            data["services"] = [
                {"name": s.service_name, "price": float(s.price)}
                for s in self.services
            ]
        return data

    def to_admin_status_dict(self):
        return {
            "merchant_id": self.merchant_id,
            "business_name": self.business_name,
            "verification_status": self.verification_status,
            "updated_at": self._format_dt(self.updated_at),
        }
