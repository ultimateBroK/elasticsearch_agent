import json
from typing import Any, Optional
import redis.asyncio as redis
import logging

from app.core.config import settings
from app.core.exceptions import RedisError
from app.core.constants import CACHE_KEYS

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching and session management."""
    
    def __init__(self):
        """Initialize Redis client."""
        # Initialize Redis client
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        logger.info(f"Redis client initialized: {settings.redis_host}:{settings.redis_port}")
    
    async def health_check(self) -> bool:
        """Check if Redis is healthy."""
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                return await self.client.setex(key, expire, value)
            else:
                return await self.client.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set key '{key}': {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Failed to get key '{key}': {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of key '{key}': {e}")
            return False
    
    async def set_session(self, session_id: str, data: dict, expire: Optional[int] = None) -> bool:
        """Set session data with expiration."""
        key = CACHE_KEYS["session"].format(session_id=session_id)
        expire = expire or settings.session_ttl
        return await self.set(key, data, expire)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = CACHE_KEYS["session"].format(session_id=session_id)
        return await self.get(key)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session data."""
        key = CACHE_KEYS["session"].format(session_id=session_id)
        return await self.delete(key)
    
    async def cache_query_result(
        self, 
        query_hash: str, 
        result: dict, 
        expire: Optional[int] = None
    ) -> bool:
        """Cache query result with expiration."""
        key = CACHE_KEYS["query"].format(query_hash=query_hash)
        expire = expire or settings.query_cache_ttl
        return await self.set(key, result, expire)
    
    async def get_cached_query(self, query_hash: str) -> Optional[dict]:
        """Get cached query result."""
        key = CACHE_KEYS["query"].format(query_hash=query_hash)
        return await self.get(key)
    
    async def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern '{pattern}': {e}")
            return 0
    
    async def close(self):
        """Close Redis connection."""
        await self.client.close()


# Note: Service instances are now managed by dependency injection
# See app.core.dependencies for service management 