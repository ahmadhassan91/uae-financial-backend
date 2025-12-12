"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List
import os
import json


# Default localhost origins for development
DEFAULT_DEV_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = ""
    DATABASE_URL_TEST: str = ""
    
    # Heroku provides DATABASE_URL automatically
    @property
    def database_url(self) -> str:
        """Get database URL, preferring Heroku's DATABASE_URL if available."""
        heroku_db_url = os.getenv("DATABASE_URL")
        if heroku_db_url:
            # Heroku uses postgres:// but SQLAlchemy needs postgresql+psycopg2://
            if heroku_db_url.startswith("postgres://"):
                heroku_db_url = heroku_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
            return heroku_db_url
        return self.DATABASE_URL
    
    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 120
    TOKEN_REFRESH_THRESHOLD_MINUTES: int = 10
    MAX_TOKEN_REFRESH_COUNT: int = 24
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS and Security - loaded from .env
    # Set CORS_ORIGINS in .env as comma-separated URLs or JSON array
    # Example: CORS_ORIGINS=https://example.com,https://app.example.com
    # Or: CORS_ORIGINS=["https://example.com","https://app.example.com"]
    CORS_ORIGINS: str = ""
    ALLOWED_HOSTS: str = ""  # Comma-separated list of allowed hosts
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get list of allowed CORS origins from environment or defaults."""
        if self.CORS_ORIGINS:
            # Try parsing as JSON array first
            try:
                origins = json.loads(self.CORS_ORIGINS)
                if isinstance(origins, list):
                    # In development, include localhost origins
                    if self.ENVIRONMENT == "development":
                        return list(set(DEFAULT_DEV_ORIGINS + origins))
                    return origins
            except json.JSONDecodeError:
                pass
            
            # Parse as comma-separated string
            origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
            if origins:
                # In development, include localhost origins
                if self.ENVIRONMENT == "development":
                    return list(set(DEFAULT_DEV_ORIGINS + origins))
                return origins
        
        # Default: only localhost origins for development
        return DEFAULT_DEV_ORIGINS
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get list of allowed hosts from environment or defaults."""
        default_hosts = [
            "localhost", 
            "127.0.0.1", 
            "0.0.0.0",
            ".herokuapp.com",  # Allow all Heroku subdomains
            ".netlify.app",    # Allow all Netlify subdomains
        ]
        if self.ALLOWED_HOSTS:
            hosts = [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]
            return list(set(default_hosts + hosts))
        return default_hosts
    
    # Email (for notifications and OTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    FROM_NAME: str = "Financial Clinic"
    
    # Redis (for caching/sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    DOWNLOAD_DIR: str = "./downloads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    USE_S3_STORAGE: bool = False  # Set to True to use S3 instead of local storage
    
    # Frontend URLs
    FRONTEND_BASE_URL: str = "http://localhost:3000"  # Development default
    PRODUCTION_BASE_URL: str = ""  # Will be loaded from .env
    BACKEND_BASE_URL: str = "http://localhost:8000"  # Backend API URL
    PRODUCTION_BACKEND_URL: str = ""  # Will be loaded from .env
    
    @property
    def base_url(self) -> str:
        """Get the appropriate base URL based on environment."""
        if self.ENVIRONMENT == "production":
            return self.PRODUCTION_BASE_URL
        return self.FRONTEND_BASE_URL
    
    @property
    def api_base_url(self) -> str:
        """Get the appropriate API base URL for backend endpoints."""
        if self.ENVIRONMENT == "production":
            return self.PRODUCTION_BACKEND_URL
        return self.BACKEND_BASE_URL
    
    @property
    def s3_pdf_base_url(self) -> str:
        """Get S3 base URL for PDF downloads."""
        if self.AWS_S3_BUCKET:
            return f"https://{self.AWS_S3_BUCKET}.s3.{self.AWS_REGION}.amazonaws.com"
        return ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
# Create global settings instance
settings = Settings()
# Ensure upload and download directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
