import os
from dotenv import load_dotenv

# Get the folder where config.py lives (the backend folder)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load variables from .env (which is one level up from backend)
load_dotenv(os.path.join(BASE_DIR, '..', '.env'))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    # Database file will be created inside backend/instance/
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'placement.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security settings for Vue compatibility
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_PASSWORD_HASH = "bcrypt"
    
    # Redis for Caching
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv('REDIS_URL')

    # Celery settings
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')