"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/uae_financial_health"
    DATABASE_URL_TEST: str = "postgresql://postgres:password@localhost:5432/uae_financial_health_test"
    
    # Heroku provides DATABASE_URL automatically
    @property
    def database_url(self) -> str:
        """Get database URL, preferring Heroku's DATABASE_URL if available."""
        heroku_db_url = os.getenv("DATABASE_URL")
        if heroku_db_url:
            # Heroku uses postgres:// but SQLAlchemy needs postgresql://
            if heroku_db_url.startswith("postgres://"):
                heroku_db_url = heroku_db_url.replace("postgres://", "postgresql://", 1)
            return heroku_db_url
        return self.DATABASE_URL
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS and Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev
        "http://localhost:3001",  # Next.js dev (alternative port)
        "http://localhost:3002",  # Next.js dev (alternative port)
        "http://localhost:3003",  # Next.js dev (alternative port)
        "http://localhost:5173",  # Vite dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:5173",
        "https://financial-clinic.netlify.app",  # Current Netlify deployment
        "https://national-bonds-ae.netlify.app",  # Specific Netlify production deployment
        "https://lively-sawine-92b143.netlify.app",  # Previous Netlify deployment
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0", "*.herokuapp.com"]
    
    # Email (for notifications and OTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    FROM_NAME: str = "National Bonds"
    
    # Redis (for caching/sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Frontend URLs
    FRONTEND_BASE_URL: str = "http://localhost:3000"  # Development default
    PRODUCTION_BASE_URL: str = "https://financial-clinic.netlify.app"  # Production URL
    
    @property
    def base_url(self) -> str:
        """Get the appropriate base URL based on environment."""
        if self.ENVIRONMENT == "production":
            return self.PRODUCTION_BASE_URL
        return self.FRONTEND_BASE_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
