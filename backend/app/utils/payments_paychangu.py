from datetime import datetime, timezone
from backend.app.models.payment import Payment
from backend.app.extensions import paychangu_client

def create_checkout_url(payment: Payment):
    # paychangu_client.initiate_tansaction(
    #     amount=payment.amount,
    #     meta={
    #         merchant_id: payment.merchant_id
    #     },
    # )
    pass

def verifiy_transaction(transaction_reference):
    pass

def generate_trans_ref(payment: Payment):
    """Create transaction refence id"""
    ref = f"{payment.merchant_id}-{payment.payment_id}-{datetime.now(timezone.utc)}"
    return ref

