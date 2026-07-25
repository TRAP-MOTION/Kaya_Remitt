from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_merchant_id():
    return f"MER{uuid.uuid4().hex[:6].upper()}"


class Merchant(db.Model):
    __tablename__ = "merchants"

    id = db.Column(db.String(36), primary_key=True, default=generate_merchant_id)
    business_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    services = db.relationship(
        "Service", backref="merchant", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_services=False):
        data = {
            "merchant_id": self.id,
            "business_name": self.business_name,
            "category": self.category,
            "location": self.location,
            "verified": self.verified,
        }
        if include_services:
            data["services"] = [s.to_dict() for s in self.services]
        return data
