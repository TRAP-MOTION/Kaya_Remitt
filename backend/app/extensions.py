from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app
from paychangu import PayChanguClient

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

_paychangu_client = None


def get_paychangu_client() -> PayChanguClient:
    """Return a process-local PayChangu client bound to current app config."""
    global _paychangu_client
    secret_key = current_app.config.get("PAYCHANGU_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("PAYCHANGU_SECRET_KEY is not configured.")

    if _paychangu_client is None or _paychangu_client.secret_key != secret_key:
        _paychangu_client = PayChanguClient(secret_key=secret_key)
    return _paychangu_client
