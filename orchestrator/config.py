"""
Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Optional API Authentication
    api_key: Optional[str] = None
    
    # Extension Configuration
    extension_timeout: int = 30
    max_concurrent_tasks: int = 5
    
    # SearXNG Configuration
    SEARXNG_URL: str = "https://searx.be"  # Public instance, or http://localhost:8080 for self-hosted
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
