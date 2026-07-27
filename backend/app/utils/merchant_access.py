"""Helpers for resolving the merchant record owned by the current user."""
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.users import User


def get_merchant_for_user(user: User) -> Merchant | None:
    """Return the verified merchant linked to this user (matched by email)."""
    if not user or not user.email:
        return None
    return db.session.execute(
        db.select(Merchant).filter_by(
            email=user.email,
            verification_status="Verified",
        )
    ).scalar_one_or_none()
