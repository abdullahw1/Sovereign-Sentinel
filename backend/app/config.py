"""
Configuration management for Sovereign Sentinel backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    you_api_key: str
    openai_api_key: str
    composio_api_key: Optional[str] = None
    
    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    scan_interval_minutes: int = 15
    
    # Cache Settings
    cache_ttl_seconds: int = 3600  # 1 hour
    
    # Risk Score Settings
    risk_threshold: int = 70
    
    # Email Notification Settings (optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    notification_from_email: Optional[str] = None
    notification_to_emails: Optional[str] = None  # Comma-separated list
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
