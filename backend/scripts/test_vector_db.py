#!/usr/bin/env python3
"""Test script for Vector Database functionality."""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_db import VectorDBService


async def test_vector_db():
    """Test Vector Database functionality."""
    print("🧪 Testing Vector Database Service...")
    
    # Initialize service
    vector_db = VectorDBService()
    
    if not vector_db.client or not vector_db.embedding_model:
        print("❌ Failed to initialize Vector DB service")
        return False
    
    print("✅ Vector DB service initialized")
    
    try:
        # Test health check
        print("\n📊 Testing health check...")
        is_healthy = await vector_db.health_check()
        print(f"Health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        # Test storing a query example
        print("\n💾 Testing query example storage...")
        query_id = await vector_db.store_query_example(
            natural_query="Show me sales data from last month",
            elasticsearch_query={
                "query": {
                    "range": {
                        "date": {
                            "gte": "2024-12-01",
                            "lte": "2024-12-31"
                        }
                    }
                }
            },
            intent="search",
            index_name="sales",
            result_count=150,
            metadata={"test": True}
        )
        
        if query_id:
            print(f"✅ Stored query example: {query_id}")
        else:
            print("❌ Failed to store query example")
            return False
        
        # Test finding similar queries
        print("\n🔍 Testing similar query search...")
        similar_queries = await vector_db.find_similar_queries(
            "Display sales information for December",
            limit=3,
            similarity_threshold=0.5
        )
        
        print(f"Found {len(similar_queries)} similar queries:")
        for i, query in enumerate(similar_queries, 1):
            print(f"  {i}. '{query['natural_query']}' (similarity: {query['similarity']:.3f})")
        
        # Test storing conversation context
        print("\n💬 Testing conversation context storage...")
        context_id = await vector_db.store_conversation_context(
            session_id="test_session_123",
            user_message="Show me sales data",
            agent_response="I found 150 sales records for you.",
            intent="search",
            query_result={"total_hits": 150, "data": []}
        )
        
        if context_id:
            print(f"✅ Stored conversation context: {context_id}")
        else:
            print("❌ Failed to store conversation context")
        
        # Test getting conversation context
        print("\n📖 Testing conversation context retrieval...")
        context_items = await vector_db.get_conversation_context(
            session_id="test_session_123",
            current_message="What about revenue data?",
            limit=3
        )
        
        print(f"Found {len(context_items)} context items:")
        for i, item in enumerate(context_items, 1):
            print(f"  {i}. User: '{item['user_message']}' -> Agent: '{item['agent_response'][:50]}...'")
        
        # Test schema storage
        print("\n🗂️ Testing schema information storage...")
        schema_id = await vector_db.store_schema_information(
            index_name="sales",
            schema={
                "mappings": {
                    "properties": {
                        "date": {"type": "date"},
                        "amount": {"type": "float"},
                        "customer": {"type": "keyword"},
                        "product": {"type": "text"}
                    }
                }
            },
            sample_data=[
                {"date": "2024-12-01", "amount": 100.0, "customer": "John", "product": "Widget A"},
                {"date": "2024-12-02", "amount": 200.0, "customer": "Jane", "product": "Widget B"}
            ]
        )
        
        if schema_id:
            print(f"✅ Stored schema information: {schema_id}")
        else:
            print("❌ Failed to store schema information")
        
        # Test getting relevant schemas
        print("\n🔎 Testing relevant schema retrieval...")
        relevant_schemas = await vector_db.get_relevant_schemas(
            "I want to analyze customer purchase patterns",
            limit=2
        )
        
        print(f"Found {len(relevant_schemas)} relevant schemas:")
        for i, schema in enumerate(relevant_schemas, 1):
            print(f"  {i}. Index: '{schema['index_name']}' (relevance: {schema['relevance']:.3f})")
        
        # Test collection statistics
        print("\n📈 Testing collection statistics...")
        stats = await vector_db.get_collection_stats()
        print("Collection statistics:")
        for collection, count in stats.items():
            print(f"  {collection}: {count} items")
        
        print("\n🎉 All Vector DB tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Vector DB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        await vector_db.close()


if __name__ == "__main__":
    success = asyncio.run(test_vector_db())
    sys.exit(0 if success else 1)