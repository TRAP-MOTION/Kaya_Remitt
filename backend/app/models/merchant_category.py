import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class MerchantCategory(db.Model):
    __tablename__ = "merchant_categories"

    category_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category_name = db.Column(db.String(100), unique=True, nullable=False)

    merchants = db.relationship(
        "Merchant", back_populates="category", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
        }
