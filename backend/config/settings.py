import os
from dotenv import load_dotenv
from pathlib import Path

config_dir = Path(__file__).parent
env_path = config_dir / ".env"
load_dotenv(env_path)

class Settings:
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes", "on")
    
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "sentry_ai_explainer")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    SENTRY_API_TOKEN = os.getenv("SENTRY_API_TOKEN", "")
    SENTRY_ORG_SLUG = os.getenv("SENTRY_ORG_SLUG", "")
    SENTRY_BASE_URL = os.getenv("SENTRY_BASE_URL", "https://sentry.io/api/0")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    APP_SENTRY_DSN = os.getenv("APP_SENTRY_DSN")
    APP_SENTRY_ENVIRONMENT = os.getenv("APP_SENTRY_ENVIRONMENT", "development")
    APP_SENTRY_RELEASE = os.getenv("APP_SENTRY_RELEASE", "1.0.0")
    APP_SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("APP_SENTRY_TRACES_SAMPLE_RATE", 0.1))
    APP_SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("APP_SENTRY_PROFILES_SAMPLE_RATE", 0.1))
    
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

settings = Settings()
