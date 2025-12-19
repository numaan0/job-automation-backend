from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

PROJECT_ROOT = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Job Application AI"
    DEBUG: bool = True
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str = str(PROJECT_ROOT / "job-auth-key.json")
    
    # Groq
    GROQ_API_KEY:str
    
    TAVILY_API_KEY: str
    
    # Model settings
    MODEL_NAME: str = "gemini-2.0-flash-exp"
    MODEL_TEMPERATURE: float = 0.3
    
    ADZUNA_APP_ID: str
    ADZUNA_APP_KEY: str
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )

@lru_cache()
def get_settings() -> Settings:
    """Cache settings to avoid reloading"""
    return Settings()
