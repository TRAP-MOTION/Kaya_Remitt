import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)

    if not SECRET_KEY or not DATABASE_URL or not JWT_SECRET_KEY:
        raise ValueError("SECRET KEY or DATABASE URL or JWT SECRET KEY is missing.")

    PAYCHANGU_SECRET_KEY = os.getenv("PAYCHANGU_SECRET_KEY")
    PAYCHANGU_CALLBACK_URL = os.getenv("PAYCHANGU_CALLBACK_URL")
    PAYCHANGU_RETURN_URL = os.getenv("PAYCHANGU_RETURN_URL")
    PAYCHANGU_CURRENCY = os.getenv("PAYCHANGU_CURRENCY", "MWK")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    PAYCHANGU_SECRET_KEY = "test-paychangu-secret"
    PAYCHANGU_CALLBACK_URL = "https://example.com/callback"
    PAYCHANGU_RETURN_URL = "https://example.com/return"
    PAYCHANGU_CURRENCY = "MWK"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
