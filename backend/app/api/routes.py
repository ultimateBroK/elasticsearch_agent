"""API routes with dependency injection."""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
import uuid
import hashlib
from datetime import datetime
import logging
import asyncio

from app.models.schemas import (
    HealthResponse, 
    ElasticsearchQuery, 
    ElasticsearchResponse,
    ChatMessage,
    ChatResponse
)
from app.core.dependencies import (
    get_elasticsearch_service,
    get_gemini_service,
    get_redis_service,
    get_vector_db_service,
    get_elasticsearch_agent
)
from app.core.exceptions import ValidationError, ElasticsearchError
from app.services.elasticsearch import ElasticsearchService
from app.services.gemini import GeminiService
from app.services.redis import RedisService
from app.services.vector_db import VectorDBService
from app.agents.elasticsearch_agent import ElasticsearchAgent
from app.utils.sample_data import setup_sample_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service),
    redis_service: RedisService = Depends(get_redis_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    vector_db_service: VectorDBService = Depends(get_vector_db_service)
):
    """Health check endpoint with dependency injection."""
    try:
        # Check service health concurrently
        es_healthy, redis_healthy, gemini_healthy, vector_db_healthy = await asyncio.gather(
            es_service.health_check(),
            redis_service.health_check(),
            gemini_service.health_check(),
            vector_db_service.health_check(),
            return_exceptions=True
        )
        
        # Handle exceptions
        es_healthy = es_healthy if not isinstance(es_healthy, Exception) else False
        redis_healthy = redis_healthy if not isinstance(redis_healthy, Exception) else False
        gemini_healthy = gemini_healthy if not isinstance(gemini_healthy, Exception) else False
        vector_db_healthy = vector_db_healthy if not isinstance(vector_db_healthy, Exception) else False
        
        # Determine overall status (vector DB is optional, so don't fail if it's down)
        core_services_healthy = es_healthy and redis_healthy and gemini_healthy
        overall_status = "healthy" if core_services_healthy else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services={
                "elasticsearch": es_healthy,
                "redis": redis_healthy,
                "gemini": gemini_healthy,
                "vector_db": vector_db_healthy
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )


@router.get("/elasticsearch/info")
async def get_elasticsearch_info(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service)
):
    """Get Elasticsearch cluster information."""
    try:
        if not await es_service.ping():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Elasticsearch is not available"
            )
        
        info = await es_service.get_cluster_info()
        return {"cluster_info": info}
        
    except Exception as e:
        logger.error(f"Failed to get Elasticsearch info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Elasticsearch information"
        )


@router.get("/elasticsearch/indices")
async def list_indices(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service)
):
    """List all Elasticsearch indices."""
    try:
        indices = await es_service.list_indices()
        return {"indices": indices}
        
    except Exception as e:
        logger.error(f"Failed to list indices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve indices"
        )


@router.post("/elasticsearch/query", response_model=ElasticsearchResponse)
async def query_elasticsearch(
    query: ElasticsearchQuery,
    es_service: ElasticsearchService = Depends(get_elasticsearch_service)
):
    """Execute Elasticsearch query."""
    try:
        # Validate input
        if not query.index:
            raise ValidationError("Index name is required")
        
        if not query.query:
            raise ValidationError("Query body is required")
        
        # Execute query
        result = await es_service.simple_search(
            index=query.index,
            query=query.query,
            size=query.size or 10
        )
        
        # Check for errors in result
        if "error" in result:
            raise ElasticsearchError(result["error"])
        
        return ElasticsearchResponse(
            total_hits=result["total_hits"],
            data=result["data"],
            aggregations=result.get("aggregations")
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ElasticsearchError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query execution failed"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    agent: ElasticsearchAgent = Depends(get_elasticsearch_agent),
    redis_service: RedisService = Depends(get_redis_service)
):
    """Chat endpoint with LangGraph Agent integration and enhanced validation."""
    try:
        # Input validation
        if not message.message or not message.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if len(message.message) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 1000 characters)"
            )
        
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Process message through the agent with timeout
        try:
            agent_result = await asyncio.wait_for(
                agent.process_message(
                    user_message=message.message.strip(),
                    session_id=session_id
                ),
                timeout=60.0  # 60 second timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Request timed out. Please try a simpler query."
            )
        
        # Store session data (non-blocking)
        try:
            session_data = {
                "last_message": message.message.strip(),
                "last_response": agent_result["response"],
                "intent": agent_result.get("intent", "general"),
                "timestamp": datetime.now().isoformat()
            }
            await redis_service.set_session(session_id, session_data)
        except Exception as redis_error:
            logger.warning(f"Failed to store session data: {redis_error}")
            # Don't fail the request for Redis issues
        
        return ChatResponse(
            response=agent_result["response"],
            session_id=session_id,
            chart_config=agent_result.get("chart_config"),
            data=agent_result.get("data", [])
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.post("/setup-sample-data")
async def setup_sample_data_endpoint(
    es_service: ElasticsearchService = Depends(get_elasticsearch_service)
):
    """Setup sample data for testing."""
    try:
        await setup_sample_data(es_service)
        return {"message": "Sample data setup completed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to setup sample data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup sample data"
        )


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """Get session data."""
    try:
        session_data = await redis_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"session": session_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session"
        )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """Delete session data."""
    try:
        success = await redis_service.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.get("/vector-db/stats")
async def get_vector_db_stats(
    vector_db_service: VectorDBService = Depends(get_vector_db_service)
):
    """Get vector database statistics."""
    try:
        stats = await vector_db_service.get_collection_stats()
        return {"stats": stats}
        
    except Exception as e:
        logger.error(f"Failed to get vector DB stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vector database statistics"
        )


@router.get("/vector-db/similar-queries")
async def find_similar_queries(
    query: str,
    limit: int = 5,
    threshold: float = 0.7,
    vector_db_service: VectorDBService = Depends(get_vector_db_service)
):
    """Find similar queries using semantic search."""
    try:
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        similar_queries = await vector_db_service.find_similar_queries(
            query, limit=min(limit, 20), similarity_threshold=max(0.0, min(1.0, threshold))
        )
        
        return {"similar_queries": similar_queries}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to find similar queries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar queries"
        )


@router.get("/intelligence/metrics")
async def get_intelligence_metrics():
    """Get intelligence service metrics and analytics."""
    try:
        from app.services.query_intelligence import query_intelligence_service
        
        metrics = await query_intelligence_service.get_intelligence_metrics()
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get intelligence metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intelligence metrics"
        )


@router.get("/intelligence/suggestions/{session_id}")
async def get_personalized_suggestions(
    session_id: str,
    context: Optional[str] = None
):
    """Get personalized suggestions for a user session."""
    try:
        from app.services.query_intelligence import query_intelligence_service
        
        suggestions = await query_intelligence_service.get_personalized_suggestions(
            session_id=session_id,
            current_context=context
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get personalized suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve personalized suggestions"
        )


@router.post("/intelligence/feedback")
async def submit_user_feedback(
    feedback_data: Dict[str, Any]
):
    """Submit user feedback for intelligence learning."""
    try:
        session_id = feedback_data.get("session_id")
        satisfaction = feedback_data.get("satisfaction", 0.5)  # 0.0 to 1.0
        chart_rating = feedback_data.get("chart_rating", 0.5)
        response_quality = feedback_data.get("response_quality", 0.5)
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )
        
        # Store feedback for learning (could be enhanced to update user profiles)
        feedback_summary = {
            "session_id": session_id,
            "satisfaction": satisfaction,
            "chart_rating": chart_rating,
            "response_quality": response_quality,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"User feedback received: {feedback_summary}")
        
        return {
            "status": "success",
            "message": "Feedback received and will be used to improve recommendations",
            "feedback_id": hashlib.md5(f"{session_id}_{datetime.now()}".encode()).hexdigest()[:8]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process user feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user feedback"
        )