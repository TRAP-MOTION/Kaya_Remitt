"""PayChangu checkout + verification helpers for KayaRemit payments."""
from __future__ import annotations

from flask import current_app
from paychangu.models.payment import Payment as PayChanguPayment

from backend.app.extensions import db, get_paychangu_client
from backend.app.models.payment import Payment
from backend.app.models.transaction import Transaction
from backend.app.models.notification import Notification
from backend.app.models.users import User


class PayChanguError(Exception):
    """Raised when PayChangu initiate/verify fails or returns an unexpected payload."""


_SUCCESS_STATUSES = {"success", "successful", "paid", "completed"}


def _split_name(full_name: str) -> tuple[str, str | None]:
    parts = (full_name or "").strip().split(None, 1)
    if not parts:
        return "Customer", None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]


def _require_paychangu_urls() -> tuple[str, str]:
    callback_url = current_app.config.get("PAYCHANGU_CALLBACK_URL")
    return_url = current_app.config.get("PAYCHANGU_RETURN_URL")
    if not callback_url or not return_url:
        raise PayChanguError(
            "PAYCHANGU_CALLBACK_URL and PAYCHANGU_RETURN_URL must be configured."
        )
    return callback_url, return_url


def _extract_checkout_url(response: dict) -> str:
    if not isinstance(response, dict):
        raise PayChanguError("Unexpected PayChangu initiate response.")

    data = response.get("data") or {}
    checkout_url = data.get("checkout_url")
    if not checkout_url:
        raise PayChanguError("PayChangu did not return a checkout_url.")
    return checkout_url


def _response_indicates_success(response: dict) -> bool:
    if not isinstance(response, dict):
        return False

    top_status = str(response.get("status") or "").lower()
    if top_status in _SUCCESS_STATUSES:
        data = response.get("data")
        if isinstance(data, dict):
            nested = str(data.get("status") or "").lower()
            if nested:
                return nested in _SUCCESS_STATUSES
        return True

    data = response.get("data")
    if isinstance(data, dict):
        nested = str(data.get("status") or "").lower()
        return nested in _SUCCESS_STATUSES

    return False


def initiate_checkout(payment: Payment, user: User) -> str:
    """Create a PayChangu hosted checkout session and return the checkout URL."""
    callback_url, return_url = _require_paychangu_urls()
    currency = current_app.config.get("PAYCHANGU_CURRENCY", "MWK")
    first_name, last_name = _split_name(user.full_name)
    amount = int(payment.amount)

    payload = PayChanguPayment(
        amount=amount,
        currency=currency,
        email=user.email,
        first_name=first_name,
        last_name=last_name,
        callback_url=callback_url,
        return_url=return_url,
        tx_ref=payment.transaction_reference,
        customization={
            "title": "KayaRemit Payment",
            "description": (
                f"Payment for {payment.beneficiary_name} "
                f"at {payment.merchant.business_name if payment.merchant else 'merchant'}"
            ),
        },
        meta={
            "payment_id": payment.payment_id,
            "merchant_id": payment.merchant_id,
            "service_id": payment.service_id,
            "user_id": user.user_id,
        },
    )

    try:
        response = get_paychangu_client().initiate_transaction(payload)
    except Exception as exc:
        raise PayChanguError(f"Failed to initiate PayChangu checkout: {exc}") from exc

    return _extract_checkout_url(response)


def verify_checkout(payment: Payment) -> bool:
    """Verify payment status with PayChangu using the stored transaction reference."""
    try:
        response = get_paychangu_client().verify_transaction(
            payment.transaction_reference
        )
    except Exception as exc:
        raise PayChanguError(f"Failed to verify PayChangu payment: {exc}") from exc

    return _response_indicates_success(response)


def simulate_merchant_payout(payment: Payment, performed_by: str) -> None:
    """Record a simulated merchant payout (sandbox does not process real payouts)."""
    db.session.add(
        Transaction(
            payment_id=payment.payment_id,
            action="PAYOUT_SIMULATED",
            performed_by=performed_by,
            status="SIMULATED",
        )
    )
    db.session.add(
        Notification(
            user_id=payment.user_id,
            title="Payout Simulated",
            message=(
                f"Merchant payout of {float(payment.amount):,.2f} "
                f"was simulated for payment {payment.transaction_reference}."
            ),
        )
    )
