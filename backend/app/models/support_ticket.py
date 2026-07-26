from datetime import datetime, timezone
import uuid
from backend.app.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    ticket_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.user_id"), nullable=False, index=True
    )
    category = db.Column(db.String(50), nullable=False, default="Support")
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open", index=True)
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="support_tickets")

    def _format_dt(self, value):
        if not value:
            return None
        formatted = value.isoformat()
        if formatted.endswith("+00:00"):
            return formatted[:-6] + "Z"
        if not formatted.endswith("Z"):
            return formatted + "Z"
        return formatted

    def to_summary_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "user_id": self.user_id,
            "category": self.category,
            "subject": self.subject,
            "status": self.status,
            "created_at": self._format_dt(self.created_at),
            "updated_at": self._format_dt(self.updated_at),
        }

    def to_dict(self):
        data = self.to_summary_dict()
        data["description"] = self.description
        data["admin_response"] = self.admin_response
        return data
