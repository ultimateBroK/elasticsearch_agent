import asyncio
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from app.services.elasticsearch import es_service
import logging

logger = logging.getLogger(__name__)


class SampleDataGenerator:
    """Generate sample data for testing the Elasticsearch Agent."""
    
    def __init__(self):
        self.products = [
            "Laptop", "Smartphone", "Tablet", "Headphones", "Smart Watch",
            "Camera", "Keyboard", "Mouse", "Monitor", "Speaker"
        ]
        
        self.regions = ["North", "South", "East", "West", "Central"]
        
        self.categories = ["Electronics", "Accessories", "Computers", "Audio", "Wearables"]
        
        self.customers = [
            "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown",
            "Frank Miller", "Grace Lee", "Henry Taylor", "Iris Chen", "Jack White"
        ]
    
    def generate_sales_data(self, num_records: int = 100) -> List[Dict[str, Any]]:
        """Generate sample sales data."""
        data = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_records):
            record = {
                "@timestamp": (base_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )).isoformat(),
                "order_id": f"ORD-{1000 + i}",
                "product_name": random.choice(self.products),
                "category": random.choice(self.categories),
                "customer_name": random.choice(self.customers),
                "region": random.choice(self.regions),
                "quantity": random.randint(1, 5),
                "unit_price": round(random.uniform(50, 1000), 2),
                "total_amount": 0,  # Will calculate below
                "discount": round(random.uniform(0, 0.2), 2),
                "status": random.choice(["completed", "pending", "cancelled"]),
                "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"]),
                "shipping_address": {
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zipcode": f"{random.randint(10000, 99999)}"
                }
            }
            
            # Calculate total amount
            subtotal = record["quantity"] * record["unit_price"]
            record["total_amount"] = round(subtotal * (1 - record["discount"]), 2)
            
            data.append(record)
        
        return data
    
    def generate_logs_data(self, num_records: int = 200) -> List[Dict[str, Any]]:
        """Generate sample application logs."""
        data = []
        base_date = datetime.now() - timedelta(days=7)
        
        log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
        services = ["api-gateway", "user-service", "payment-service", "inventory-service"]
        
        for i in range(num_records):
            level = random.choice(log_levels)
            service = random.choice(services)
            
            record = {
                "@timestamp": (base_date + timedelta(
                    hours=random.randint(0, 168),  # 7 days
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )).isoformat(),
                "level": level,
                "service": service,
                "message": f"Sample {level.lower()} message from {service}",
                "request_id": f"req-{random.randint(100000, 999999)}",
                "user_id": f"user-{random.randint(1, 100)}",
                "response_time_ms": random.randint(10, 5000),
                "status_code": random.choice([200, 201, 400, 401, 404, 500]),
                "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible; TestAgent/1.0)"
            }
            
            data.append(record)
        
        return data
    
    async def create_index_with_mapping(self, index_name: str, mapping: Dict[str, Any]):
        """Create index with proper mapping."""
        try:
            # Check if index exists
            exists = await es_service.client.indices.exists(index=index_name)
            
            if exists:
                logger.info(f"Index '{index_name}' already exists, skipping creation")
                return
            
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
            
            logger.info(f"Created index '{index_name}' with mapping")
            
        except Exception as e:
            logger.error(f"Failed to create index '{index_name}': {e}")
            raise
    
    async def bulk_insert_data(self, index_name: str, data: List[Dict[str, Any]]):
        """Bulk insert data into Elasticsearch."""
        try:
            # Prepare bulk request
            bulk_body = []
            
            for doc in data:
                bulk_body.append({"index": {"_index": index_name}})
                bulk_body.append(doc)
            
            # Execute bulk request
            response = await es_service.client.bulk(
                body=bulk_body,
                refresh=True
            )
            
            if response.get("errors"):
                logger.warning(f"Some documents failed to index in '{index_name}'")
            else:
                logger.info(f"Successfully indexed {len(data)} documents in '{index_name}'")
            
        except Exception as e:
            logger.error(f"Failed to bulk insert data into '{index_name}': {e}")
            raise
    
    async def setup_sample_indices(self):
        """Setup all sample indices with data."""
        try:
            # Sales data index
            sales_mapping = {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "order_id": {"type": "keyword"},
                    "product_name": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "customer_name": {"type": "keyword"},
                    "region": {"type": "keyword"},
                    "quantity": {"type": "integer"},
                    "unit_price": {"type": "float"},
                    "total_amount": {"type": "float"},
                    "discount": {"type": "float"},
                    "status": {"type": "keyword"},
                    "payment_method": {"type": "keyword"},
                    "shipping_address": {
                        "properties": {
                            "city": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "zipcode": {"type": "keyword"}
                        }
                    }
                }
            }
            
            # Logs data index
            logs_mapping = {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "request_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "response_time_ms": {"type": "integer"},
                    "status_code": {"type": "integer"},
                    "ip_address": {"type": "ip"},
                    "user_agent": {"type": "text"}
                }
            }
            
            # Create indices
            await self.create_index_with_mapping("sample-sales", sales_mapping)
            await self.create_index_with_mapping("sample-logs", logs_mapping)
            
            # Generate and insert data
            sales_data = self.generate_sales_data(100)
            logs_data = self.generate_logs_data(200)
            
            await self.bulk_insert_data("sample-sales", sales_data)
            await self.bulk_insert_data("sample-logs", logs_data)
            
            logger.info("Successfully set up all sample indices")
            
        except Exception as e:
            logger.error(f"Failed to setup sample indices: {e}")
            raise


# Utility function to run sample data setup
async def setup_sample_data():
    """Main function to setup sample data."""
    generator = SampleDataGenerator()
    await generator.setup_sample_indices()


if __name__ == "__main__":
    asyncio.run(setup_sample_data()) 