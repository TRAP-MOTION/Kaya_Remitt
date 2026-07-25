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

    cfg = config.get(config_name, config["default"])
    app.config.from_object(cfg)

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)

    # Ensure all models are registered with SQLAlchemy metadata
    import backend.app.models  # noqa: F401

    _register_blueprints(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.user import user_bp
    from backend.app.routes.merchants import merchants_bp
    from backend.app.routes.payments import payments_bp
    from backend.app.routes.vouchers import vouchers_bp
    from backend.app.routes.merchant_dashboard import merchant_dashboard_bp

    prefix = "/api/v1"

    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(user_bp, url_prefix=f"{prefix}")
    app.register_blueprint(merchants_bp, url_prefix=f"{prefix}/merchants")
    app.register_blueprint(payments_bp, url_prefix=f"{prefix}/payments")
    app.register_blueprint(vouchers_bp, url_prefix=f"{prefix}/vouchers")
    app.register_blueprint(merchant_dashboard_bp, url_prefix=f"{prefix}/merchant")
