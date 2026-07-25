import uuid
from backend.app.extensions import db


def generate_service_id():
    return f"SER{uuid.uuid4().hex[:6].upper()}"


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.String(36), primary_key=True, default=generate_service_id)
    merchant_id = db.Column(
        db.String(36), db.ForeignKey("merchants.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "service_id": self.id,
            "name": self.name,
            "amount": round(float(self.amount), 2),
        }
