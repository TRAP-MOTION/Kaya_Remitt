import os
from dotenv import load_dotenv

load_dotenv()


def _fix_postgres_url(url: str | None) -> str | None:
    """SQLAlchemy 1.4+ requires 'postgresql://' not 'postgres://'."""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = _fix_postgres_url(os.getenv("DATABASE_URL"))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or SECRET_KEY
    FLASK_ENV = "development"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

    PAYCHANGU_SECRET_KEY = os.getenv("PAYCHANGU_SECRET_KEY")
    PAYCHANGU_CALLBACK_URL = os.getenv("PAYCHANGU_CALLBACK_URL")
    PAYCHANGU_RETURN_URL = os.getenv("PAYCHANGU_RETURN_URL")
    PAYCHANGU_CURRENCY = os.getenv("PAYCHANGU_CURRENCY", "MWK")

    # Connection pool tuning for PostgreSQL in production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # drop stale connections automatically
        "pool_recycle": 300,     # recycle connections every 5 minutes
        "pool_size": 10,
        "max_overflow": 20,
    }


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig:
    """Standalone config for unit tests — no real DB or external service needed."""
    SECRET_KEY = "test-secret-key"
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    JWT_SECRET_KEY = "test-jwt-secret-key"
    FLASK_ENV = "testing"
    TESTING = True
    DEBUG = False
    ALLOWED_ORIGINS = None

    PAYCHANGU_SECRET_KEY = "test-paychangu-secret"
    PAYCHANGU_CALLBACK_URL = "https://example.com/callback"
    PAYCHANGU_RETURN_URL = "https://example.com/return"
    PAYCHANGU_CURRENCY = "MWK"

    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def validate_config(cfg) -> None:
    """Raise ValueError if required production config values are missing."""
    required = {
        "SECRET_KEY": cfg.SECRET_KEY,
        "DATABASE_URL": cfg.DATABASE_URL,
        "JWT_SECRET_KEY": cfg.JWT_SECRET_KEY,
        "PAYCHANGU_SECRET_KEY": cfg.PAYCHANGU_SECRET_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required config values: {', '.join(missing)}")
