from typing import Dict, Any, List, Optional
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import logging

from app.core.config import settings
from app.core.exceptions import ElasticsearchError

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Elasticsearch service for handling ES operations."""
    
    def __init__(self):
        """Initialize Elasticsearch client."""
        # Build connection parameters
        connection_params = {
            "hosts": [settings.elasticsearch_url],
            "request_timeout": 30,
            "retry_on_timeout": True,
            "max_retries": 3,
        }
        
        # Add authentication if provided
        if settings.elasticsearch_username and settings.elasticsearch_password:
            connection_params["basic_auth"] = (
                settings.elasticsearch_username,
                settings.elasticsearch_password
            )
        
        # Initialize client with connection pooling
        self.client = AsyncElasticsearch(**connection_params)
        
        logger.info(f"Elasticsearch client initialized: {settings.elasticsearch_url}")
    
    async def health_check(self) -> bool:
        """Check if Elasticsearch is healthy."""
        try:
            health = await self.client.cluster.health()
            return health["status"] in ["green", "yellow"]
        except ConnectionError:
            logger.error("Failed to connect to Elasticsearch")
            return False
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False
    
    async def ping(self) -> bool:
        """Ping Elasticsearch server."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Elasticsearch ping failed: {e}")
            return False
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        try:
            info = await self.client.info()
            return {
                "cluster_name": info.get("cluster_name"),
                "cluster_uuid": info.get("cluster_uuid"),
                "version": info.get("version", {}).get("number"),
                "lucene_version": info.get("version", {}).get("lucene_version")
            }
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return {}
    
    async def list_indices(self) -> List[str]:
        """List all indices."""
        try:
            response = await self.client.cat.indices(format="json")
            return [index["index"] for index in response if not index["index"].startswith(".")]
        except Exception as e:
            logger.error(f"Failed to list indices: {e}")
            return []
    
    async def simple_search(
        self, 
        index: str, 
        query: Dict[str, Any], 
        size: int = 10
    ) -> Dict[str, Any]:
        """Perform simple search on Elasticsearch with enhanced error handling."""
        # Input validation
        if not index or not isinstance(index, str):
            raise ValueError("Invalid index name")
        
        if not query or not isinstance(query, dict):
            raise ValueError("Invalid query structure")
        
        # Clamp size to reasonable limits
        size = max(0, min(settings.max_query_size, size))
        
        try:
            response = await self.client.search(
                index=index,
                body=query,
                size=size,
                timeout="30s"  # Add timeout
            )
            
            # Handle different total hit formats (ES 7.x vs 8.x)
            total_hits = response["hits"]["total"]
            if isinstance(total_hits, dict):
                total_count = total_hits.get("value", 0)
            else:
                total_count = total_hits
            
            return {
                "total_hits": total_count,
                "data": [hit["_source"] for hit in response["hits"]["hits"]],
                "aggregations": response.get("aggregations", {}),
                "took": response.get("took", 0),
                "timed_out": response.get("timed_out", False)
            }
        except NotFoundError:
            logger.error(f"Index '{index}' not found")
            return {
                "total_hits": 0,
                "data": [],
                "aggregations": {},
                "error": f"Index '{index}' not found"
            }
        except Exception as e:
            logger.error(f"Search failed for index '{index}': {e}")
            return {
                "total_hits": 0,
                "data": [],
                "aggregations": {},
                "error": f"Search failed: {str(e)}"
            }
    
    async def aggregate_data(
        self, 
        index: str, 
        aggregations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform aggregation query."""
        try:
            query = {
                "size": 0,
                "aggs": aggregations
            }
            
            response = await self.client.search(
                index=index,
                body=query
            )
            
            return response.get("aggregations", {})
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            raise
    
    async def count_documents(self, index: str, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in index."""
        try:
            body = {"query": query} if query else {}
            response = await self.client.count(index=index, body=body)
            return response["count"]
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0
    
    async def close(self):
        """Close Elasticsearch connection."""
        await self.client.close()


# Note: Service instances are now managed by dependency injection
# See app.core.dependencies for service management 