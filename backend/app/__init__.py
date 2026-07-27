import os
from flask import Flask
from backend.app.config import config, validate_config
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

    if config_name not in ("testing",):
        validate_config(cfg)

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = getattr(cfg, "SQLALCHEMY_ENGINE_OPTIONS", {})

    db.init_app(app)
    migrate.init_app(app, db)
    _setup_cors(app, cfg)
    limiter.init_app(app)

    # Ensure all models are registered with SQLAlchemy metadata
    import backend.app.models  # noqa: F401

    _register_blueprints(app)

    return app


def _setup_cors(app: Flask, cfg) -> None:
    """Configure Flask-CORS.

    In production ALLOWED_ORIGINS restricts which origins may call the API.
    In development/testing all origins are permitted.
    """
    origins = getattr(cfg, "ALLOWED_ORIGINS", None)
    if origins:
        # Support comma-separated list: "https://app.example.com,https://www.example.com"
        origin_list = [o.strip() for o in origins.split(",") if o.strip()]
        cors.init_app(
            app,
            resources={r"/api/*": {"origins": origin_list}},
            supports_credentials=True,
        )
    else:
        cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def _register_blueprints(app: Flask) -> None:
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.user import user_bp
    from backend.app.routes.merchants import merchants_bp
    from backend.app.routes.payments import payments_bp
    from backend.app.routes.vouchers import vouchers_bp
    from backend.app.routes.merchant_dashboard import merchant_dashboard_bp
    from backend.app.routes.admin import admin_bp
    from backend.app.routes.notifications import notifications_bp

    prefix = "/api/v1"

    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(user_bp, url_prefix=f"{prefix}")
    app.register_blueprint(merchants_bp, url_prefix=f"{prefix}/merchants")
    app.register_blueprint(payments_bp, url_prefix=f"{prefix}/payments")
    app.register_blueprint(vouchers_bp, url_prefix=f"{prefix}/vouchers")
    app.register_blueprint(merchant_dashboard_bp, url_prefix=f"{prefix}/merchant")
    app.register_blueprint(admin_bp, url_prefix=f"{prefix}/admin")
    app.register_blueprint(notifications_bp, url_prefix=f"{prefix}/notifications")
