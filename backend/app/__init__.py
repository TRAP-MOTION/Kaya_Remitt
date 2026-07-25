import os
from flask import Flask
from backend.app.config import config
from backend.app.extensions import db, migrate, cors, limiter


def create_app(config_name: str | None = None) -> Flask:
    """Flask application factory.

    Args:
        config_name: One of 'development', 'testing', 'production', or 'default'.
                     Reads the FLASK_ENV environment variable when not provided.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)

    # Load config object
    cfg = config.get(config_name, config["default"])
    app.config.from_object(cfg)

    # SQLAlchemy requires SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)

    # Register blueprints under /api/v1
    _register_blueprints(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.user import user_bp
    from backend.app.routes.wallet import wallet_bp
    from backend.app.routes.notification import notification_bp
    from backend.app.routes.budget import budget_bp
    from backend.app.routes.goal import goal_bp
    from backend.app.routes.merchants import merchants_bp
    from backend.app.routes.payments import payments_bp
    from backend.app.routes.vouchers import vouchers_bp
    from backend.app.routes.merchant_dashboard import merchant_dashboard_bp

    prefix = "/api/v1"

    # Auth
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")

    # User profile — spec: /api/v1/profile and /api/v1/pin
    app.register_blueprint(user_bp, url_prefix=f"{prefix}")

    # Wallet (peer-to-peer transfers — not in spec but retained)
    app.register_blueprint(wallet_bp, url_prefix=f"{prefix}/wallet")

    # Notifications (not in spec but retained)
    app.register_blueprint(notification_bp, url_prefix=f"{prefix}/notifications")

    # Budget (not in spec but retained)
    app.register_blueprint(budget_bp, url_prefix=f"{prefix}/budget")

    # Goals (not in spec but retained)
    app.register_blueprint(goal_bp, url_prefix=f"{prefix}/goals")

    # Merchants — spec: /api/v1/merchants
    app.register_blueprint(merchants_bp, url_prefix=f"{prefix}/merchants")

    # Payments — spec: /api/v1/payments
    app.register_blueprint(payments_bp, url_prefix=f"{prefix}/payments")

    # Vouchers — spec: /api/v1/vouchers
    app.register_blueprint(vouchers_bp, url_prefix=f"{prefix}/vouchers")

    # Merchant dashboard — spec: /api/v1/merchant/...
    app.register_blueprint(merchant_dashboard_bp, url_prefix=f"{prefix}/merchant")
