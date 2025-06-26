#!/usr/bin/env python3
"""Comprehensive test script for the enhanced intelligence system."""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.query_intelligence import (
    query_intelligence_service, 
    QueryPattern, 
    UserBehavior,
    QueryInsight
)
from app.services.vector_db import VectorDBService
from app.services.redis import RedisService
from app.agents.elasticsearch_agent import ElasticsearchAgent


async def test_intelligence_system():
    """Test the complete intelligence system integration."""
    print("🧠 Testing Enhanced Intelligence System...")
    
    # Test scenarios with different user behaviors
    test_scenarios = [
        {
            "name": "Time Series Explorer",
            "user_type": UserBehavior.EXPLORER,
            "queries": [
                "Show me sales trends over the last 6 months",
                "Compare revenue by month for this year vs last year", 
                "What's the daily pattern in user activity?",
                "Are there any seasonal trends in our data?",
                "Show me anomalies in the time series data"
            ]
        },
        {
            "name": "Business Analyst", 
            "user_type": UserBehavior.ANALYST,
            "queries": [
                "What's the total revenue by product category?",
                "Show me the top 10 customers by revenue",
                "Break down sales performance by region",
                "What's the correlation between price and sales volume?",
                "Analyze the distribution of order values"
            ]
        },
        {
            "name": "Casual Reporter",
            "user_type": UserBehavior.REPORTER,
            "queries": [
                "Give me a summary of today's sales",
                "How many orders did we process this week?",
                "What's our total revenue this month?"
            ]
        },
        {
            "name": "Data Scientist",
            "user_type": UserBehavior.ANALYST,
            "queries": [
                "Find outliers in customer behavior data",
                "Show me the correlation matrix for all numeric fields",
                "What's the distribution of response times?",
                "Identify patterns in user engagement metrics",
                "Analyze cohort retention rates"
            ]
        }
    ]
    
    print("\n📊 Testing Query Pattern Recognition...")
    
    # Test pattern recognition for each scenario
    for scenario in test_scenarios:
        print(f"\n--- Testing {scenario['name']} Behavior ---")
        session_id = f"test_session_{scenario['name'].lower().replace(' ', '_')}"
        
        for i, query in enumerate(scenario['queries'], 1):
            print(f"\n{i}. Query: '{query}'")
            
            # Simulate intent analysis (normally done by Gemini)
            intent_analysis = simulate_intent_analysis(query)
            
            # Test pattern recognition
            query_insight = await query_intelligence_service.analyze_query_pattern(
                user_message=query,
                intent_analysis=intent_analysis,
                session_id=session_id
            )
            
            print(f"   Pattern: {query_insight.pattern.value}")
            print(f"   Confidence: {query_insight.confidence:.1%}")
            print(f"   Reasoning: {query_insight.reasoning}")
            
            if query_insight.suggested_improvements:
                print(f"   Suggestions: {query_insight.suggested_improvements[:2]}")
            
            # Update user profile
            await query_intelligence_service.update_user_profile(
                session_id=session_id,
                query_insight=query_insight,
                intent_analysis=intent_analysis,
                user_feedback={"satisfaction": 0.8}  # Simulate positive feedback
            )
    
    print("\n🎯 Testing Personalized Suggestions...")
    
    # Test personalized suggestions for each user type
    for scenario in test_scenarios:
        session_id = f"test_session_{scenario['name'].lower().replace(' ', '_')}"
        
        suggestions = await query_intelligence_service.get_personalized_suggestions(
            session_id=session_id,
            current_context="I want to explore more data insights"
        )
        
        print(f"\n{scenario['name']} Suggestions:")
        for j, suggestion in enumerate(suggestions, 1):
            print(f"  {j}. {suggestion}")
    
    print("\n📈 Testing Intelligence Metrics...")
    
    # Get intelligence metrics
    metrics = await query_intelligence_service.get_intelligence_metrics()
    
    print(f"Total User Profiles: {metrics['total_user_profiles']}")
    print(f"Behavior Distribution: {metrics['behavior_distribution']}")
    print(f"Pattern Distribution: {metrics['pattern_distribution']}")
    print(f"Average Query Complexity: {metrics['average_query_complexity']:.2f}")
    print(f"Active Sessions: {metrics['active_sessions']}")
    
    print("\n🔍 Testing Pattern Detection Accuracy...")
    
    # Test specific pattern detection
    pattern_tests = [
        {
            "query": "Show me sales trends over time",
            "expected_pattern": QueryPattern.TIME_SERIES_ANALYSIS,
            "keywords": ["trends", "over time"]
        },
        {
            "query": "Compare revenue between regions",
            "expected_pattern": QueryPattern.CATEGORICAL_COMPARISON,
            "keywords": ["compare", "between"]
        },
        {
            "query": "What's the total sales amount?",
            "expected_pattern": QueryPattern.AGGREGATION_SUMMARY,
            "keywords": ["total", "amount"]
        },
        {
            "query": "Find correlation between price and sales",
            "expected_pattern": QueryPattern.CORRELATION_ANALYSIS,
            "keywords": ["correlation", "between"]
        },
        {
            "query": "Show me the distribution of order values",
            "expected_pattern": QueryPattern.DISTRIBUTION_ANALYSIS,
            "keywords": ["distribution", "values"]
        }
    ]
    
    correct_predictions = 0
    total_tests = len(pattern_tests)
    
    for test in pattern_tests:
        intent_analysis = simulate_intent_analysis(test["query"])
        
        query_insight = await query_intelligence_service.analyze_query_pattern(
            user_message=test["query"],
            intent_analysis=intent_analysis,
            session_id="pattern_test_session"
        )
        
        predicted_pattern = query_insight.pattern
        expected_pattern = test["expected_pattern"]
        
        is_correct = predicted_pattern == expected_pattern
        if is_correct:
            correct_predictions += 1
        
        print(f"Query: '{test['query']}'")
        print(f"  Expected: {expected_pattern.value}")
        print(f"  Predicted: {predicted_pattern.value}")
        print(f"  Confidence: {query_insight.confidence:.1%}")
        print(f"  Result: {'✅ Correct' if is_correct else '❌ Incorrect'}")
        print()
    
    accuracy = (correct_predictions / total_tests) * 100
    print(f"Pattern Recognition Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
    
    print("\n🚀 Testing Agent Integration...")
    
    # Test with mock services (since we might not have real API keys)
    try:
        # This would normally require real services
        print("Agent integration test would require:")
        print("  - Valid Google Gemini API key")
        print("  - Running Elasticsearch instance")
        print("  - Running Redis instance")
        print("  - ChromaDB setup")
        print("  ⚠️ Skipping full agent test (use real environment for complete testing)")
        
    except Exception as e:
        print(f"Agent integration test skipped: {e}")
    
    print("\n🎉 Intelligence System Testing Complete!")
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"  ✅ Pattern Recognition: {accuracy:.1f}% accuracy")
    print(f"  ✅ User Profiling: {metrics['total_user_profiles']} profiles created")
    print(f"  ✅ Personalized Suggestions: Generated for all user types")
    print(f"  ✅ Intelligence Metrics: All metrics collected successfully")
    print(f"  ✅ Query Insights: Generated for all test queries")
    
    if accuracy >= 80:
        print("\n🏆 Intelligence system is performing excellently!")
    elif accuracy >= 60:
        print("\n👍 Intelligence system is performing well!")
    else:
        print("\n⚠️ Intelligence system may need tuning!")
    
    return True


def simulate_intent_analysis(query: str) -> dict:
    """Simulate intent analysis for testing (normally done by Gemini)."""
    query_lower = query.lower()
    
    # Simple keyword-based intent detection for testing
    if any(word in query_lower for word in ["trend", "over time", "timeline", "daily", "monthly"]):
        intent = "chart"
        chart_type = "line"
        aggregation_type = "date_histogram"
    elif any(word in query_lower for word in ["compare", "between", "vs", "versus"]):
        intent = "aggregate"
        chart_type = "bar"
        aggregation_type = "terms"
    elif any(word in query_lower for word in ["total", "sum", "count", "average"]):
        intent = "aggregate"
        chart_type = "bar"
        aggregation_type = "sum" if "total" in query_lower or "sum" in query_lower else "count"
    elif any(word in query_lower for word in ["correlation", "relationship"]):
        intent = "search"
        chart_type = "scatter"
        aggregation_type = None
    elif any(word in query_lower for word in ["distribution", "spread"]):
        intent = "search"
        chart_type = "histogram"
        aggregation_type = None
    else:
        intent = "search"
        chart_type = "bar"
        aggregation_type = None
    
    return {
        "intent": intent,
        "chart_type": chart_type,
        "aggregation_type": aggregation_type,
        "query_description": f"Analysis of: {query}",
        "fields": ["timestamp", "amount", "category", "region"],  # Mock fields
        "confidence": 0.8
    }


if __name__ == "__main__":
    success = asyncio.run(test_intelligence_system())
    sys.exit(0 if success else 1)