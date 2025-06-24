"""Vector database service using ChromaDB for semantic search and memory."""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib
import json

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class VectorDBService:
    """ChromaDB service for semantic search and query memory."""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collections
            self._initialize_collections()
            
            logger.info("ChromaDB service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB service: {e}")
            self.client = None
            self.embedding_model = None
    
    def _initialize_collections(self):
        """Initialize ChromaDB collections."""
        try:
            # Collection for storing query examples and patterns
            self.query_collection = self.client.get_or_create_collection(
                name="query_examples",
                metadata={"description": "Natural language query examples with ES DSL mappings"}
            )
            
            # Collection for storing conversation context
            self.context_collection = self.client.get_or_create_collection(
                name="conversation_context",
                metadata={"description": "Conversation context and user preferences"}
            )
            
            # Collection for storing data schema information
            self.schema_collection = self.client.get_or_create_collection(
                name="data_schemas",
                metadata={"description": "Elasticsearch index schemas and field mappings"}
            )
            
            logger.info("ChromaDB collections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if ChromaDB service is healthy."""
        if not self.client or not self.embedding_model:
            return False
        
        try:
            # Test basic operations
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.heartbeat
            )
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    
    async def close(self):
        """Close ChromaDB connections."""
        try:
            if self.client:
                # ChromaDB doesn't have explicit close method
                # Data is persisted automatically
                logger.info("ChromaDB service closed")
        except Exception as e:
            logger.error(f"Error closing ChromaDB: {e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    async def store_query_example(
        self,
        natural_query: str,
        elasticsearch_query: Dict[str, Any],
        intent: str,
        index_name: str,
        result_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a query example for future semantic search."""
        try:
            # Generate unique ID
            query_id = hashlib.md5(
                f"{natural_query}_{json.dumps(elasticsearch_query, sort_keys=True)}".encode()
            ).hexdigest()
            
            # Generate embedding
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, natural_query
            )
            
            if not embedding:
                logger.error("Failed to generate embedding for query")
                return None
            
            # Prepare document
            document = {
                "natural_query": natural_query,
                "elasticsearch_query": json.dumps(elasticsearch_query),
                "intent": intent,
                "index_name": index_name,
                "result_count": result_count,
                "metadata": json.dumps(metadata or {})
            }
            
            # Store in ChromaDB
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.query_collection.upsert,
                [query_id],
                [embedding],
                [document]
            )
            
            logger.info(f"Stored query example: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to store query example: {e}")
            return None
    
    async def find_similar_queries(
        self,
        natural_query: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar queries using semantic search."""
        try:
            if not self.client or not self.embedding_model:
                return []
            
            # Generate embedding for query
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, natural_query
            )
            
            if not query_embedding:
                return []
            
            # Search for similar queries
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.query_collection.query,
                query_embedding,
                limit
            )
            
            similar_queries = []
            
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    similarity = 1.0 - distance  # Convert distance to similarity
                    
                    if similarity >= similarity_threshold:
                        metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                        
                        similar_queries.append({
                            "id": results['ids'][0][i],
                            "natural_query": metadata.get("natural_query", ""),
                            "elasticsearch_query": json.loads(metadata.get("elasticsearch_query", "{}")),
                            "intent": metadata.get("intent", "unknown"),
                            "index_name": metadata.get("index_name", ""),
                            "similarity": similarity,
                            "metadata": json.loads(metadata.get("metadata", "{}"))
                        })
            
            logger.info(f"Found {len(similar_queries)} similar queries for: {natural_query}")
            return similar_queries
            
        except Exception as e:
            logger.error(f"Failed to find similar queries: {e}")
            return []
    
    async def store_conversation_context(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        intent: str,
        query_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store conversation context for multi-turn conversations."""
        try:
            # Generate unique ID
            context_id = f"{session_id}_{hashlib.md5(user_message.encode()).hexdigest()}"
            
            # Create context text for embedding
            context_text = f"User: {user_message}\nAgent: {agent_response}"
            
            # Generate embedding
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, context_text
            )
            
            if not embedding:
                return None
            
            # Prepare document
            document = {
                "session_id": session_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "intent": intent,
                "query_result": json.dumps(query_result or {}),
                "context_text": context_text
            }
            
            # Store in ChromaDB
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.context_collection.upsert,
                [context_id],
                [embedding],
                [document]
            )
            
            logger.info(f"Stored conversation context: {context_id}")
            return context_id
            
        except Exception as e:
            logger.error(f"Failed to store conversation context: {e}")
            return None
    
    async def get_conversation_context(
        self,
        session_id: str,
        current_message: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get relevant conversation context for current message."""
        try:
            if not self.client or not self.embedding_model:
                return []
            
            # Generate embedding for current message
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, current_message
            )
            
            if not query_embedding:
                return []
            
            # Search for relevant context
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.context_collection.query,
                query_embedding,
                limit,
                {"session_id": session_id}  # Filter by session
            )
            
            context_items = []
            
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    context_items.append({
                        "user_message": metadata.get("user_message", ""),
                        "agent_response": metadata.get("agent_response", ""),
                        "intent": metadata.get("intent", "unknown"),
                        "query_result": json.loads(metadata.get("query_result", "{}")),
                        "relevance": 1.0 - (results['distances'][0][i] if results['distances'] else 1.0)
                    })
            
            return context_items
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []
    
    async def store_schema_information(
        self,
        index_name: str,
        schema: Dict[str, Any],
        sample_data: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Store Elasticsearch index schema information."""
        try:
            # Generate unique ID
            schema_id = f"schema_{index_name}"
            
            # Create description text for embedding
            field_descriptions = []
            if "mappings" in schema and "properties" in schema["mappings"]:
                for field, props in schema["mappings"]["properties"].items():
                    field_type = props.get("type", "unknown")
                    field_descriptions.append(f"{field} ({field_type})")
            
            description_text = f"Index: {index_name}\nFields: {', '.join(field_descriptions)}"
            
            # Generate embedding
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, description_text
            )
            
            if not embedding:
                return None
            
            # Prepare document
            document = {
                "index_name": index_name,
                "schema": json.dumps(schema),
                "sample_data": json.dumps(sample_data or []),
                "description": description_text,
                "field_count": len(field_descriptions)
            }
            
            # Store in ChromaDB
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.schema_collection.upsert,
                [schema_id],
                [embedding],
                [document]
            )
            
            logger.info(f"Stored schema information for index: {index_name}")
            return schema_id
            
        except Exception as e:
            logger.error(f"Failed to store schema information: {e}")
            return None
    
    async def get_relevant_schemas(
        self,
        query_description: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get relevant index schemas based on query description."""
        try:
            if not self.client or not self.embedding_model:
                return []
            
            # Generate embedding for query description
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_embedding, query_description
            )
            
            if not query_embedding:
                return []
            
            # Search for relevant schemas
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.schema_collection.query,
                query_embedding,
                limit
            )
            
            schemas = []
            
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    schemas.append({
                        "index_name": metadata.get("index_name", ""),
                        "schema": json.loads(metadata.get("schema", "{}")),
                        "sample_data": json.loads(metadata.get("sample_data", "[]")),
                        "description": metadata.get("description", ""),
                        "relevance": 1.0 - (results['distances'][0][i] if results['distances'] else 1.0)
                    })
            
            return schemas
            
        except Exception as e:
            logger.error(f"Failed to get relevant schemas: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        try:
            if not self.client:
                return {}
            
            stats = {}
            
            # Get collection counts
            for collection_name, collection in [
                ("query_examples", self.query_collection),
                ("conversation_context", self.context_collection),
                ("data_schemas", self.schema_collection)
            ]:
                try:
                    count = await asyncio.get_event_loop().run_in_executor(
                        None, collection.count
                    )
                    stats[collection_name] = count
                except Exception as e:
                    logger.error(f"Failed to get count for {collection_name}: {e}")
                    stats[collection_name] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}


# Note: Service instances are now managed by dependency injection
# See app.core.dependencies for service management