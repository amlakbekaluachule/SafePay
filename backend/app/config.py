"""Configuration settings for SafePay."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SafePay Fraud Detection API"
    VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/safepay"
    
    MODEL_PATH: str = "models/fraud_detector.pkl"
    FEATURE_METADATA_PATH: str = "models/feature_metadata.json"
    
    FEATURE_STORE_ENABLED: bool = True
    
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

