"""
Sample data ingestion script for Elasticsearch
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.elasticsearch import ElasticsearchService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_sample_sales_data() -> List[Dict[str, Any]]:
    """Generate sample sales data for testing."""
    products = [
        "iPhone 15", "Samsung Galaxy S24", "MacBook Pro", "Dell XPS",
        "iPad Air", "Surface Pro", "AirPods Pro", "Sony WH-1000XM5",
        "Monitor 4K", "Gaming Mouse", "Mechanical Keyboard", "Webcam HD"
    ]
    
    regions = ["North", "South", "East", "West", "Central"]
    sales_people = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson",
        "David Brown", "Lisa Garcia", "Tom Anderson", "Emma Taylor"
    ]
    
    data = []
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(1000):  # Generate 1000 sample records
        sale_date = start_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        record = {
            "id": f"sale_{i+1:04d}",
            "product": random.choice(products),
            "region": random.choice(regions),
            "salesperson": random.choice(sales_people),
            "amount": round(random.uniform(100, 2000), 2),
            "quantity": random.randint(1, 10),
            "date": sale_date.isoformat(),
            "status": random.choice(["completed", "pending", "cancelled"]),
            "customer_type": random.choice(["individual", "business"]),
            "payment_method": random.choice(["credit_card", "cash", "bank_transfer"]),
            "discount": round(random.uniform(0, 20), 1),  # Discount percentage
            "created_at": sale_date.isoformat()
        }
        data.append(record)
    
    return data


def generate_sample_logs_data() -> List[Dict[str, Any]]:
    """Generate sample log data for testing."""
    log_levels = ["INFO", "DEBUG", "WARN", "ERROR"]
    services = ["api-gateway", "user-service", "payment-service", "inventory-service"]
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(5000):  # Generate 5000 log records
        log_date = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        record = {
            "id": f"log_{i+1:06d}",
            "timestamp": log_date.isoformat(),
            "level": random.choice(log_levels),
            "service": random.choice(services),
            "message": f"Log message {i+1}",
            "user_id": f"user_{random.randint(1, 1000):04d}",
            "request_id": f"req_{random.randint(1, 10000):06d}",
            "duration_ms": random.randint(10, 5000),
            "status_code": random.choice([200, 201, 400, 401, 404, 500]),
            "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "created_at": log_date.isoformat()
        }
        data.append(record)
    
    return data


async def create_index_with_mapping(index_name: str, mapping: Dict[str, Any]):
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


async def ingest_bulk_data(index_name: str, documents: List[Dict[str, Any]]):
    """Ingest documents in bulk."""
    try:
        # Prepare bulk body
        bulk_body = []
        for doc in documents:
            bulk_body.append({"index": {"_index": index_name}})
            bulk_body.append(doc)
        
        # Execute bulk insert
        response = await es_service.client.bulk(
            body=bulk_body,
            refresh=True  # Make documents immediately available for search
        )
        
        if response["errors"]:
            logger.error(f"Bulk insert had errors: {response}")
        else:
            logger.info(f"Successfully inserted {len(documents)} documents into {index_name}")
            
        return response
        
    except Exception as e:
        logger.error(f"Error during bulk insert: {e}")
        raise


async def setup_sample_data(es_service=None):
    """Setup all sample data."""
    logger.info("Starting sample data setup...")
    
    # Initialize service if not provided
    if es_service is None:
        es_service = ElasticsearchService()
    
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
            "status": {"type": "keyword"},
            "customer_type": {"type": "keyword"},
            "payment_method": {"type": "keyword"},
            "discount": {"type": "float"},
            "created_at": {"type": "date"}
        }
    }
    
    # Logs data mapping
    logs_mapping = {
        "properties": {
            "id": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "level": {"type": "keyword"},
            "service": {"type": "keyword"},
            "message": {"type": "text"},
            "user_id": {"type": "keyword"},
            "request_id": {"type": "keyword"},
            "duration_ms": {"type": "integer"},
            "status_code": {"type": "integer"},
            "ip_address": {"type": "ip"},
            "created_at": {"type": "date"}
        }
    }
    
    try:
        # Create sales index and ingest data
        await create_index_with_mapping("sales", sales_mapping)
        sales_data = generate_sample_sales_data()
        await ingest_bulk_data("sales", sales_data)
        
        # Create logs index and ingest data
        await create_index_with_mapping("logs", logs_mapping)
        logs_data = generate_sample_logs_data()
        await ingest_bulk_data("logs", logs_data)
        
        logger.info("Sample data setup completed successfully!")
        
        # Print summary
        sales_count = await es_service.client.count(index="sales")
        logs_count = await es_service.client.count(index="logs")
        
        logger.info(f"Sales documents: {sales_count['count']}")
        logger.info(f"Logs documents: {logs_count['count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up sample data: {e}")
        return False


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
