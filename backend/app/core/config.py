"""Application configuration management."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    app_name: str = Field(default="Elasticsearch Agent API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # Elasticsearch
    elasticsearch_host: str = Field(default="localhost", env="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    elasticsearch_scheme: str = Field(default="http", env="ELASTICSEARCH_SCHEME")
    elasticsearch_username: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    
    # Redis
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Google Gemini API
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Cache settings
    query_cache_ttl: int = Field(default=300, env="QUERY_CACHE_TTL")  # 5 minutes
    session_ttl: int = Field(default=3600, env="SESSION_TTL")  # 1 hour
    
    # Agent settings
    max_query_size: int = Field(default=1000, env="MAX_QUERY_SIZE")
    default_chart_type: str = Field(default="bar", env="DEFAULT_CHART_TYPE")
    
    @property
    def elasticsearch_url(self) -> str:
        """Get full Elasticsearch URL."""
        return f"{self.elasticsearch_scheme}://{self.elasticsearch_host}:{self.elasticsearch_port}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()