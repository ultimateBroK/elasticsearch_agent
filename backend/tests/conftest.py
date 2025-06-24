"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import Settings
from app.core.dependencies import initialize_services, cleanup_services
from main import create_app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Test settings configuration."""
    return Settings(
        google_api_key="test_key",
        elasticsearch_host="localhost",
        elasticsearch_port=9200,
        redis_host="localhost",
        redis_port=6379,
        debug=True
    )


@pytest.fixture(scope="session")
async def app():
    """Create test FastAPI application."""
    test_app = create_app()
    yield test_app


@pytest.fixture(scope="session")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def sync_client(app):
    """Create synchronous test client."""
    return TestClient(app)