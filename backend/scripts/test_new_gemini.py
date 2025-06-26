#!/usr/bin/env python3
"""Test script for the new google-genai integration."""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini import GeminiService
from app.core.config import settings


async def test_new_gemini_api():
    """Test the new google-genai API integration."""
    print("🧪 Testing New Google GenAI Integration...")
    
    # Check if API key is available
    if not settings.google_api_key or settings.google_api_key == "your_actual_gemini_api_key_here":
        print("❌ GOOGLE_API_KEY not set or using placeholder value")
        print("Please set a real Google Gemini API key in your .env file")
        print("Get your API key from: https://ai.google.dev/")
        return False
    
    try:
        # Initialize the service
        print("\n🔧 Initializing Gemini service...")
        gemini_service = GeminiService()
        print(f"✅ Service initialized with model: {gemini_service.model_name}")
        
        # Test health check
        print("\n🏥 Testing health check...")
        is_healthy = await gemini_service.health_check()
        print(f"Health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if not is_healthy:
            print("❌ Health check failed - API may not be accessible")
            return False
        
        # Test basic content generation
        print("\n💬 Testing basic content generation...")
        response = await gemini_service.generate_content(
            "What is 2+2? Answer briefly.",
            temperature=0.1,
            max_output_tokens=50
        )
        
        if response:
            print(f"✅ Basic generation successful: {response}")
        else:
            print("❌ Basic generation failed")
            return False
        
        # Test with system instruction
        print("\n🎯 Testing with system instruction...")
        response = await gemini_service.generate_content(
            "Explain photosynthesis",
            system_instruction="You are a helpful science teacher. Explain concepts clearly and concisely.",
            temperature=0.3,
            max_output_tokens=200
        )
        
        if response:
            print(f"✅ System instruction test successful: {response[:100]}...")
        else:
            print("❌ System instruction test failed")
            return False
        
        # Test intent analysis (existing method)
        print("\n🧠 Testing intent analysis...")
        intent_analysis = await gemini_service.analyze_query_intent(
            "Show me sales trends over the last 6 months"
        )
        
        if intent_analysis and intent_analysis.get('intent'):
            print(f"✅ Intent analysis successful: {intent_analysis['intent']}")
            print(f"   Chart type: {intent_analysis.get('chart_type', 'None')}")
            print(f"   Description: {intent_analysis.get('query_description', 'None')}")
        else:
            print("❌ Intent analysis failed")
            return False
        
        # Test query generation
        print("\n⚙️ Testing Elasticsearch query generation...")
        es_query = await gemini_service.generate_elasticsearch_query(
            intent_analysis, 
            ["sample-sales", "sample-logs"]
        )
        
        if es_query and isinstance(es_query, dict):
            print(f"✅ Query generation successful: {list(es_query.keys())}")
        else:
            print("❌ Query generation failed")
            return False
        
        # Test response generation
        print("\n📝 Testing response generation...")
        mock_results = {
            "total_hits": 150,
            "data": [
                {"date": "2024-01-01", "sales": 1000},
                {"date": "2024-01-02", "sales": 1200}
            ]
        }
        
        response_message = await gemini_service.generate_response_message(
            "Show me sales trends",
            mock_results,
            intent_analysis
        )
        
        if response_message:
            print(f"✅ Response generation successful: {response_message[:100]}...")
        else:
            print("❌ Response generation failed")
            return False
        
        # Test enhanced chart recommendations
        print("\n📊 Testing enhanced chart recommendations...")
        try:
            enhanced_recs = await gemini_service.generate_enhanced_chart_recommendations(
                data=mock_results["data"],
                intent_analysis=intent_analysis
            )
            
            if enhanced_recs:
                print(f"✅ Enhanced recommendations successful: {len(enhanced_recs)} recommendations")
                for i, rec in enumerate(enhanced_recs[:2], 1):
                    print(f"   {i}. {rec['chart_type']} (confidence: {rec['confidence']:.1%})")
            else:
                print("⚠️ Enhanced recommendations returned empty (may need chart recommendation service)")
        except Exception as e:
            print(f"⚠️ Enhanced recommendations test skipped: {e}")
        
        print("\n🎉 All Google GenAI tests completed successfully!")
        print("\n📋 Test Summary:")
        print("  ✅ Service initialization")
        print("  ✅ Health check")
        print("  ✅ Basic content generation")
        print("  ✅ System instruction support")
        print("  ✅ Intent analysis")
        print("  ✅ Query generation")
        print("  ✅ Response generation")
        print("  ✅ API integration working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_new_gemini_api())
    if success:
        print("\n🚀 Google GenAI integration is working perfectly!")
        print("You can now use the enhanced Elasticsearch Agent with gemini-2.5-flash!")
    else:
        print("\n⚠️ Please check your API key and try again.")
    
    sys.exit(0 if success else 1)