#!/usr/bin/env python3
"""Fixed sample data ingestion script."""

import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.elasticsearch import ElasticsearchService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_index_with_mapping(es_service: ElasticsearchService, index_name: str, mapping: Dict[str, Any]):
    """Create index with proper mapping."""
    try:
        # Delete index if exists
        try:
            await es_service.client.indices.delete(index=index_name)
            logger.info(f"Deleted existing index: {index_name}")
        except Exception:
            pass
        
        # Create index with mapping
        await es_service.client.indices.create(
            index=index_name,
            body={
                "mappings": mapping,
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
        )
        logger.info(f"Created index: {index_name}")
        
    except Exception as e:
        logger.error(f"Error creating index {index_name}: {e}")
        raise


async def bulk_index_data(es_service: ElasticsearchService, index_name: str, data: List[Dict[str, Any]]):
    """Bulk index data to Elasticsearch."""
    try:
        # Prepare bulk data
        bulk_data = []
        for doc in data:
            bulk_data.append({"index": {"_index": index_name}})
            bulk_data.append(doc)
        
        # Bulk index
        response = await es_service.client.bulk(
            body=bulk_data,
            refresh=True
        )
        
        # Check for errors
        if response.get("errors"):
            logger.error(f"Bulk indexing errors for {index_name}")
            for item in response["items"]:
                if "error" in item.get("index", {}):
                    logger.error(f"Error: {item['index']['error']}")
        else:
            logger.info(f"Successfully indexed {len(data)} documents to {index_name}")
            
    except Exception as e:
        logger.error(f"Error bulk indexing to {index_name}: {e}")
        raise


async def setup_sample_data():
    """Setup all sample data."""
    logger.info("Starting sample data setup...")
    
    # Initialize service
    es_service = ElasticsearchService()
    
    try:
        # Check ES connection
        if not await es_service.ping():
            logger.error("Cannot connect to Elasticsearch")
            return False
        
        # Sales data mapping
        sales_mapping = {
            "properties": {
                "id": {"type": "keyword"},
                "product": {"type": "keyword"},
                "region": {"type": "keyword"},
                "salesperson": {"type": "keyword"},
                "amount": {"type": "float"},
                "quantity": {"type": "integer"},
                "date": {"type": "date"},
                "customer_type": {"type": "keyword"}
            }
        }
        
        # Logs data mapping
        logs_mapping = {
            "properties": {
                "timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "message": {"type": "text"},
                "service": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "ip_address": {"type": "ip"},
                "response_time": {"type": "integer"},
                "status_code": {"type": "integer"}
            }
        }
        
        # Create indices
        await create_index_with_mapping(es_service, "sales", sales_mapping)
        await create_index_with_mapping(es_service, "logs", logs_mapping)
        
        # Generate sales data
        sales_data = []
        products = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Z"]
        regions = ["North", "South", "East", "West", "Central"]
        salespeople = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        customer_types = ["Enterprise", "SMB", "Individual"]
        
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(500):
            sales_data.append({
                "id": f"sale_{i+1:04d}",
                "product": products[i % len(products)],
                "region": regions[i % len(regions)],
                "salesperson": salespeople[i % len(salespeople)],
                "amount": round(100 + (i * 10.5) % 1000, 2),
                "quantity": (i % 10) + 1,
                "date": (base_date + timedelta(days=i % 90)).isoformat(),
                "customer_type": customer_types[i % len(customer_types)]
            })
        
        # Generate logs data
        logs_data = []
        services = ["api", "web", "auth", "payment", "notification"]
        levels = ["INFO", "WARN", "ERROR", "DEBUG"]
        
        for i in range(1000):
            logs_data.append({
                "timestamp": (base_date + timedelta(hours=i % (24*7))).isoformat(),
                "level": levels[i % len(levels)],
                "message": f"Sample log message {i+1}",
                "service": services[i % len(services)],
                "user_id": f"user_{(i % 100) + 1:03d}",
                "ip_address": f"192.168.{(i % 255) + 1}.{(i % 254) + 1}",
                "response_time": (i % 1000) + 50,
                "status_code": [200, 201, 400, 404, 500][i % 5]
            })
        
        # Index data
        await bulk_index_data(es_service, "sales", sales_data)
        await bulk_index_data(es_service, "logs", logs_data)
        
        # Verify data
        sales_count = await es_service.client.count(index="sales")
        logs_count = await es_service.client.count(index="logs")
        
        logger.info(f"Sales documents: {sales_count['count']}")
        logger.info(f"Logs documents: {logs_count['count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up sample data: {e}")
        return False
    
    finally:
        # Close service
        await es_service.close()


async def main():
    """Main function."""
    success = await setup_sample_data()
    if success:
        logger.info("✅ Sample data ingestion completed successfully!")
    else:
        logger.error("❌ Sample data ingestion failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())