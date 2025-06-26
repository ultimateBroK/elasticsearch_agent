"""
Test script for Gemini API integration
"""
import os
import asyncio
import sys

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_gemini_basic():
    """Test basic Gemini API functionality."""
    try:
        import google.genai as genai
         
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("❌ GOOGLE_API_KEY environment variable not set!")
            logger.info("Please set your Gemini API key:")
            logger.info("export GOOGLE_API_KEY='your-api-key-here'")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test basic generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Testing basic text generation...")
        response = await model.generate_content_async("Hello, how are you?")
        logger.info(f"✅ Gemini response: {response.text}")
        
        return True
        
    except ImportError:
        logger.error("❌ google-genai package not installed!")
        logger.info("Please install: uv add google-genai>=1.21.1")
        return False
    except Exception as e:
        logger.error(f"❌ Gemini API test failed: {e}")
        return False


async def test_gemini_elasticsearch_query():
    """Test Gemini for Elasticsearch query generation."""
    try:
        import google.genai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Testing Elasticsearch query generation...")
        
        prompt = """
        Convert this natural language query to Elasticsearch DSL JSON:
        "Show me total sales by region for the last 30 days"
        
        Available fields: region, amount, date, product, salesperson
        Index: sales
        
        Return only valid JSON DSL query.
        """
        
        response = await model.generate_content_async(prompt)
        logger.info("✅ Generated ES Query:")
        logger.info(response.text)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ES query generation test failed: {e}")
        return False


async def test_gemini_chart_recommendation():
    """Test Gemini for chart type recommendation."""
    try:
        import google.genai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Testing chart recommendation...")
        
        prompt = """
        Based on this data query result, recommend the best chart type:
        
        Query: "Total sales by region"
        Data structure: {
            "aggregations": {
                "regions": {
                    "doc_count": 1000,
                    "buckets": [
                        {"key": "North", "doc_count": 200, "total_sales": {"value": 45000}},
                        {"key": "South", "doc_count": 180, "total_sales": {"value": 38000}},
                        {"key": "East", "doc_count": 220, "total_sales": {"value": 52000}},
                        {"key": "West", "doc_count": 190, "total_sales": {"value": 41000}},
                        {"key": "Central", "doc_count": 210, "total_sales": {"value": 47000}}
                    ]
                }
            }
        }
        
        Choose from: line, bar, pie, scatter, heatmap
        Return only the chart type name and brief reason.
        """
        
        response = await model.generate_content_async(prompt)
        logger.info("✅ Chart recommendation:")
        logger.info(response.text)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chart recommendation test failed: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting Gemini API integration tests...")
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Basic functionality
    if await test_gemini_basic():
        success_count += 1
    
    # Test 2: ES query generation
    if await test_gemini_elasticsearch_query():
        success_count += 1
    
    # Test 3: Chart recommendation
    if await test_gemini_chart_recommendation():
        success_count += 1
    
    logger.info(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        logger.info("✅ All Gemini API tests passed!")
        return True
    else:
        logger.info("❌ Some tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
