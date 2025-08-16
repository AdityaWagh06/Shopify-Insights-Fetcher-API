import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Shopify Insights-Fetcher"
    PROJECT_DESCRIPTION: str = "API for scraping data from Shopify websites"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Server settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings (optional)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()