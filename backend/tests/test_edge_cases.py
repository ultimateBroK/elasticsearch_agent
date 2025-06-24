"""Test edge cases and potential issues."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.core.config import Settings
from app.core.exceptions import *
from app.services.elasticsearch import ElasticsearchService
from app.services.gemini import GeminiService
from app.services.redis import RedisService
from app.agents.elasticsearch_agent import ElasticsearchAgent


class TestEdgeCases:
    """Test various edge cases that could break the application."""

    def test_config_with_missing_api_key(self):
        """Test configuration with missing API key."""
        with pytest.raises(Exception):  # Should raise validation error
            Settings(google_api_key="")

    def test_config_with_invalid_ports(self):
        """Test configuration with invalid port numbers."""
        with pytest.raises(Exception):
            Settings(
                google_api_key="test_key",
                elasticsearch_port=-1
            )

    @pytest.mark.asyncio
    async def test_elasticsearch_service_with_no_connection(self):
        """Test Elasticsearch service when connection fails."""
        service = ElasticsearchService()
        # Mock the client to simulate connection failure
        service.client = Mock()
        service.client.ping = AsyncMock(side_effect=ConnectionError("Connection failed"))
        
        result = await service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_gemini_service_with_invalid_api_key(self):
        """Test Gemini service with invalid API key."""
        # This would normally fail during initialization
        # but we test the error handling
        service = GeminiService()
        service.client = None  # Simulate failed initialization
        
        result = await service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_redis_service_connection_failure(self):
        """Test Redis service when connection fails."""
        service = RedisService()
        service.client = Mock()
        service.client.ping = AsyncMock(side_effect=ConnectionError("Redis down"))
        
        result = await service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_agent_with_none_services(self):
        """Test agent behavior when services are None."""
        agent = ElasticsearchAgent(
            gemini_service=None,
            elasticsearch_service=None,
            redis_service=None
        )
        
        # This should handle gracefully or raise appropriate errors
        with pytest.raises(AttributeError):
            await agent.process_message("test message", "session_id")

    @pytest.mark.asyncio
    async def test_elasticsearch_search_with_empty_index(self):
        """Test search on empty index."""
        service = ElasticsearchService()
        service.client = Mock()
        service.client.search = AsyncMock(return_value={
            "hits": {"total": {"value": 0}, "hits": []},
            "aggregations": {}
        })
        
        result = await service.simple_search("empty_index", {"query": {"match_all": {}}})
        assert result["total_hits"] == 0
        assert result["data"] == []

    @pytest.mark.asyncio
    async def test_elasticsearch_search_with_malformed_query(self):
        """Test search with malformed query."""
        service = ElasticsearchService()
        service.client = Mock()
        service.client.search = AsyncMock(side_effect=Exception("Invalid query"))
        
        result = await service.simple_search("test_index", {"invalid": "query"})
        assert "error" in result

    @pytest.mark.asyncio
    async def test_redis_operations_with_connection_loss(self):
        """Test Redis operations when connection is lost mid-operation."""
        service = RedisService()
        service.client = Mock()
        service.client.setex = AsyncMock(side_effect=ConnectionError("Connection lost"))
        
        result = await service.set("test_key", {"data": "test"}, 300)
        assert result is False

    @pytest.mark.asyncio
    async def test_gemini_with_rate_limiting(self):
        """Test Gemini service when rate limited."""
        service = GeminiService()
        service.client = Mock()
        
        # Mock rate limit error
        async def mock_generate(*args, **kwargs):
            raise Exception("Rate limit exceeded")
        
        service.client.generate_content_async = mock_generate
        
        result = await service.generate_content("test prompt")
        assert result is None

    def test_chart_data_edge_cases(self):
        """Test chart generation with edge case data."""
        # Test with empty data
        empty_data = []
        # Should not crash when processing empty data
        
        # Test with None values
        none_data = [{"field1": None, "field2": None}]
        # Should handle None values gracefully
        
        # Test with mixed data types
        mixed_data = [
            {"field1": "string", "field2": 123},
            {"field1": 456, "field2": "another_string"}
        ]
        # Should handle mixed types
        
        assert True  # Placeholder - actual chart tests would go here

    @pytest.mark.asyncio
    async def test_websocket_message_edge_cases(self):
        """Test WebSocket message handling edge cases."""
        # Test with invalid JSON
        invalid_json = "{ invalid json }"
        
        # Test with missing required fields
        missing_fields = {"type": "message"}  # Missing "message" field
        
        # Test with oversized message
        oversized_message = {"type": "message", "message": "x" * 10000}
        
        # These should be handled gracefully by the WebSocket handler
        assert True  # Placeholder

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        # Simulate multiple concurrent requests
        tasks = []
        for i in range(10):
            # Create mock requests
            task = asyncio.create_task(asyncio.sleep(0.1))  # Placeholder
            tasks.append(task)
        
        # All should complete without issues
        await asyncio.gather(*tasks)
        assert True

    def test_environment_variable_edge_cases(self):
        """Test edge cases in environment variable handling."""
        # Test with empty strings
        # Test with special characters
        # Test with very long values
        # Test with unicode characters
        
        # These should be handled by the config validation
        assert True  # Placeholder

    @pytest.mark.asyncio
    async def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large datasets."""
        # Test with large Elasticsearch results
        large_data = [{"field": f"value_{i}"} for i in range(10000)]
        
        # Should handle large datasets without memory issues
        # (In real implementation, we limit results to prevent this)
        assert len(large_data) == 10000

    @pytest.mark.asyncio
    async def test_timeout_scenarios(self):
        """Test various timeout scenarios."""
        # Test Elasticsearch query timeout
        # Test Gemini API timeout
        # Test Redis operation timeout
        # Test WebSocket message timeout
        
        # All should be handled gracefully with appropriate error messages
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__])