import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    APP_NAME: str = "Paint Shop API"
    DEBUG: bool = False
    
    # Bảo mật
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sqlite_data/app.db")
    
    # Logs
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()