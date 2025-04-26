import os
import logging
from flask import Flask
from typing import Optional, List

from app.utils.helpers.basics import parse_bool
from app.utils.date_time import timedelta

class Config:
    ENV: str = os.getenv("ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-dev-secret")  # Warn in prod
    # Add these CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = True  # Enable if using HTTPS
    
    # Session settings
    SESSION_COOKIE_SECURE = True  # Enable if using HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SERVER_NAME: Optional[str] = os.getenv("FLASK_SERVER_NAME")
    PREFERRED_URL_SCHEME: Optional[str] = os.getenv("FLASK_URL_SCHEME", "http")
    
    
    DEBUG: bool = parse_bool(os.getenv("DEBUG")) or (ENV == "development") # Enable debug mode only in development
    EMERGENCY_MODE: bool = parse_bool(os.getenv("EMERGENCY_MODE", False))
    
    CLIENT_ORIGINS: List[str] = [
        origin.strip() for origin in 
        os.getenv("CLIENT_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    ]
    
    # Security credentials (use a vault in production)
    DEFAULT_SUPER_ADMIN_USERNAME: Optional[str] = os.getenv("DEFAULT_SUPER_ADMIN_USERNAME")
    DEFAULT_SUPER_ADMIN_PASSWORD: Optional[str] = os.getenv("DEFAULT_SUPER_ADMIN_PASSWORD")
    
    # JWT configurations
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)  # Fallback to SECRET_KEY
    
    # mail configurations
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_SSL: bool = parse_bool(os.getenv("MAIL_USE_SSL", "false"))
    MAIL_USE_TLS: bool = parse_bool(os.getenv("MAIL_USE_TLS", "true"))
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: Optional[str] = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    MAIL_ALIAS = (f"{MAIL_DEFAULT_SENDER}", f"{MAIL_USERNAME}")
    
    # Domains
    API_DOMAIN_NAME: str = os.getenv("API_DOMAIN_NAME", "http://localhost:5000")
    APP_DOMAIN_NAME: str = os.getenv("APP_DOMAIN_NAME", "http://localhost:5000")
    
    
    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    
    
    #  ExchangeRate-API
    EXCHANGE_RATE_API_KEY: Optional[str] = os.getenv("EXCHANGE_RATE_API_KEY")
    EXCHANGE_RATE_API_URL: str = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///dev.db")

class ProductionConfig(Config):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL")  # No default; enforce env var
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Recommended for security

class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "mysql+pymysql://root:@localhost:3301/bitnshop?charset=utf8mb4"


# Map config based on environment
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

def configure_logging(app: Flask) -> None:
    """Replace Flask's default logging with a custom setup."""
    
    # Remove all handlers
    app.logger.handlers.clear()
    
    if not app.logger.handlers:
        formatter = logging.Formatter("[%(asctime)s] ==> %(levelname)s in %(module)s: %(message)s")
        
        # Stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
    
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO) # Set the desired logging level