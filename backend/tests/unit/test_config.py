"""Test configuration management."""

import pytest
from app.core.config import Settings


def test_settings_creation():
    """Test settings creation with default values."""
    settings = Settings(google_api_key="test_key")
    
    assert settings.app_name == "Elasticsearch Agent API"
    assert settings.elasticsearch_host == "localhost"
    assert settings.elasticsearch_port == 9200
    assert settings.redis_host == "localhost"
    assert settings.redis_port == 6379


def test_elasticsearch_url():
    """Test Elasticsearch URL generation."""
    settings = Settings(
        google_api_key="test_key",
        elasticsearch_host="es.example.com",
        elasticsearch_port=9200,
        elasticsearch_scheme="https"
    )
    
    assert settings.elasticsearch_url == "https://es.example.com:9200"


def test_redis_url():
    """Test Redis URL generation."""
    settings = Settings(
        google_api_key="test_key",
        redis_host="redis.example.com",
        redis_port=6379,
        redis_password="secret"
    )
    
    assert settings.redis_url == "redis://:secret@redis.example.com:6379/0"


def test_redis_url_no_password():
    """Test Redis URL generation without password."""
    settings = Settings(
        google_api_key="test_key",
        redis_host="redis.example.com",
        redis_port=6379
    )
    
    assert settings.redis_url == "redis://redis.example.com:6379/0"