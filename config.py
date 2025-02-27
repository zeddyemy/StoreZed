import os, logging
from flask import Flask

class Config:
    ENV = os.getenv("ENV") or "development"
    SECRET_KEY = os.getenv("SECRET_KEY") or os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = "9395-105-115-3-2.ngrok-free.app" or os.getenv("FLASK_SERVER_NAME")
    PREFERRED_URL_SCHEME = os.getenv("FLASK_URL_SCHEME")
    
    DEBUG = (ENV == "development")  # Enable debug mode only in development
    EMERGENCY_MODE = os.getenv("EMERGENCY_MODE") or os.environ.get("EMERGENCY_MODE") or False
    
    CLIENT_ORIGINS = os.getenv("CLIENT_ORIGINS") or os.environ.get("CLIENT_ORIGINS") or "http://localhost:3000,http://localhost:5173"
    CLIENT_ORIGINS = [origin.strip() for origin in CLIENT_ORIGINS.split(",")]
    
    DEFAULT_SUPER_ADMIN_USERNAME = os.getenv("DEFAULT_SUPER_ADMIN_USERNAME")
    DEFAULT_SUPER_ADMIN_PASSWORD = os.getenv("DEFAULT_SUPER_ADMIN_PASSWORD")
    
    # JWT configurations
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.environ.get('JWT_SECRET_KEY')
    
    # mail configurations
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get("MAIL_PORT") or 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_ALIAS = (f"{MAIL_DEFAULT_SENDER}", f"{MAIL_USERNAME}")
    
    # Domains
    API_DOMAIN_NAME = os.environ.get("API_DOMAIN_NAME") or "https://9395-105-115-3-2.ngrok-free.app"
    APP_DOMAIN_NAME = os.environ.get("APP_DOMAIN_NAME") or "https://9395-105-115-3-2.ngrok-free.app"
    
    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or "dcozguaw3"
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or "798295575458768"
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or "HwXtPdaC5M1zepKZUriKCYZ9tsI"
    
    #  ExchangeRate-API
    EXCHANGE_RATE_API_KEY = os.environ.get("EXCHANGE_RATE_API_KEY")
    EXCHANGE_RATE_API_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest"
    

class DevelopmentConfig(Config):
    FLASK_DEBUG = True
    DEBUG_TOOLBAR = True  # Enable debug toolbar
    EXPOSE_DEBUG_SERVER = False  # Do not expose debugger publicly
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or os.getenv("DATABASE_URL")

class ProductionConfig(Config):
    DEBUG = False
    FLASK_DEBUG = False
    DEBUG_TOOLBAR = False
    EXPOSE_DEBUG_SERVER = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3301/bitnshop?charset=utf8mb4"


# Map config based on environment
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

def configure_logging(app: Flask):
    if not app.logger.handlers:
        formatter = logging.Formatter("[%(asctime)s] ==> %(levelname)s in %(module)s: %(message)s")
        
        # Stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
        
        app.logger.setLevel(logging.DEBUG)  # Set the desired logging level