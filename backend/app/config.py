"""Configuration settings for SafePay."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SafePay Fraud Detection API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/safepay"
    
    # ML Model
    MODEL_PATH: str = "models/fraud_detector.pkl"
    FEATURE_METADATA_PATH: str = "models/feature_metadata.json"
    
    # Feature Store
    FEATURE_STORE_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

