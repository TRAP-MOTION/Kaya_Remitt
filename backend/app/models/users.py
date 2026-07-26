from datetime import datetime, timezone
import uuid
from backend.app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="diaspora")
    account_status = db.Column(db.String(20), nullable=False, default="Active")
    country = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    payments = db.relationship("Payment", back_populates="user", lazy="dynamic")
    notifications = db.relationship(
        "Notification", back_populates="user", lazy="dynamic"
    )
    support_tickets = db.relationship(
        "SupportTicket", back_populates="user", lazy="dynamic"
    )

    @property
    def is_active(self):
        return self.account_status.lower() == "active"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        formatted_date = self.created_at.isoformat()
        if formatted_date.endswith("+00:00"):
            formatted_date = formatted_date[:-6] + "Z"
        elif not formatted_date.endswith("Z"):
            formatted_date += "Z"
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "account_status": self.account_status,
            "country": self.country,
            "created_at": formatted_date,
        }
