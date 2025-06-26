import logging
from typing import List, Dict, Any, Optional
import asyncio
import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import GeminiAPIError, ConfigurationError
from app.services.chart_recommendation import chart_recommendation_service, ChartRecommendation

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API using google-genai."""
    
    def __init__(self):
        """Initialize Gemini client."""
        if not settings.google_api_key:
            raise ConfigurationError("GOOGLE_API_KEY not found in environment variables")
        
        try:
            # Create the new google-genai client
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model_name = 'gemini-2.0-flash'  # Using gemini-2.5-flash as requested
            
            logger.info(f"Gemini client initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Failed to initialize Gemini client: {e}")
    
    async def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        if not self.client:
            return False
        
        try:
            # Simple test message with timeout
            response = await self.generate_content(
                "Hello", 
                temperature=0.1, 
                max_output_tokens=10
            )
            return response is not None and len(response.strip()) > 0
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
    
    async def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1000,
        retry_count: int = 3
    ) -> Optional[str]:
        """Generate content using Gemini with retry logic."""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        # Input validation
        if not prompt or not prompt.strip():
            logger.error("Empty prompt provided")
            return None
        
        for attempt in range(retry_count):
            try:
                # Prepare the content - combine system instruction and prompt
                full_content = prompt.strip()
                if system_instruction:
                    full_content = f"{system_instruction.strip()}\n\n{prompt.strip()}"
                
                # Create generation config
                config = types.GenerateContentConfig(
                    temperature=max(0.0, min(2.0, temperature)),
                    max_output_tokens=max(1, min(8192, max_output_tokens)),
                )
                
                # Generate content using the new API
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_content,
                        config=config
                    )
                )
                
                if response and response.text:
                    result = response.text.strip()
                    if result:  # Ensure non-empty response
                        return result
                
                logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                
            except Exception as e:
                logger.error(f"Gemini content generation failed on attempt {attempt + 1}: {e}")
                if attempt == retry_count - 1:  # Last attempt
                    return None
                
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def analyze_query_intent(
        self, 
        user_message: str,
        similar_queries: Optional[List[Dict[str, Any]]] = None,
        conversation_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze user message to determine intent and extract parameters with enhanced context."""
        system_instruction = """
        You are an expert at analyzing user queries for Elasticsearch operations with semantic understanding.
        
        Given a user message, conversation context, and similar queries, identify:
        1. Intent: search, aggregate, filter, chart, count, or general
        2. Index: which elasticsearch index to query (if mentioned)
        3. Time range: any time-based filters
        4. Fields: relevant fields mentioned
        5. Chart type: if user wants visualization (line, bar, pie, scatter, area)
        6. Aggregation: type of aggregation needed (terms, date_histogram, avg, sum, etc.)
        7. Context relevance: how this relates to previous conversation
        8. Confidence: how confident you are in the analysis (0.0-1.0)
        
        Use similar queries and conversation context to improve accuracy.
        Learn from successful patterns and adapt to user preferences.
        
        Respond with a JSON object containing these fields.
        If uncertain, make reasonable assumptions based on context.
        
        Available sample indices: sample-sales, sample-logs
        """
        
        # Build context information
        context_info = ""
        if similar_queries:
            context_info += "\nSimilar successful queries:\n"
            for i, query in enumerate(similar_queries[:3], 1):
                context_info += f"{i}. '{query['natural_query']}' -> {query['intent']} (similarity: {query['similarity']:.2f})\n"
        
        if conversation_context:
            context_info += "\nRecent conversation context:\n"
            for i, ctx in enumerate(conversation_context[:2], 1):
                context_info += f"{i}. User: '{ctx['user_message']}' -> Intent: {ctx['intent']}\n"
        
        prompt = f"""
        User message: "{user_message}"
        {context_info}
        
        Analyze this message and return a JSON response with:
        {{
            "intent": "search|aggregate|filter|chart|count|general",
            "index": "index_name or null",
            "time_range": "last_30_days|last_week|today|null",
            "fields": ["field1", "field2"] or null,
            "chart_type": "line|bar|pie|scatter|area|null",
            "aggregation_type": "terms|date_histogram|avg|sum|count|null",
            "query_description": "brief description of what user wants",
            "context_relevance": "how this relates to previous conversation",
            "confidence": 0.8
        }}
        """
        
        try:
            response = await self.generate_content(prompt, system_instruction, temperature=0.3)
            
            if response:
                # Try to parse JSON from response with better extraction
                parsed_json = self._extract_json_from_response(response)
                if parsed_json:
                    # Validate required fields
                    return self._validate_intent_analysis(parsed_json)
            
            # Fallback if parsing fails
            return self._get_fallback_intent_analysis("Unable to parse intent")
            
        except Exception as e:
            logger.error(f"Failed to analyze query intent: {e}")
            return self._get_fallback_intent_analysis("Error analyzing intent")
    
    async def generate_elasticsearch_query(
        self, 
        intent_analysis: Dict[str, Any],
        available_indices: List[str]
    ) -> Dict[str, Any]:
        """Generate Elasticsearch query based on intent analysis."""
        system_instruction = """
        You are an expert at generating Elasticsearch queries.
        
        Based on the intent analysis, generate a proper Elasticsearch query JSON.
        Consider:
        - Use appropriate query types (match, term, range, bool)
        - Add proper aggregations for charts and summaries
        - Handle time ranges correctly
        - Use realistic field names based on the context
        
        Return only valid Elasticsearch query JSON.
        """
        
        prompt = f"""
        Intent analysis: {json.dumps(intent_analysis, indent=2)}
        Available indices: {available_indices}
        
        Generate an Elasticsearch query for this intent.
        
        For sample-sales index, common fields are:
        - @timestamp, product_name, category, region, total_amount, quantity, status
        
        For sample-logs index, common fields are:
        - @timestamp, level, service, response_time_ms, status_code
        
        Return a JSON query object.
        """
        
        try:
            response = await self.generate_content(prompt, system_instruction, temperature=0.2)
            
            if response:
                # Extract JSON from response
                response = response.strip()
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    return json.loads(json_str)
            
            # Fallback simple query
            return {"query": {"match_all": {}}}
            
        except Exception as e:
            logger.error(f"Failed to generate ES query: {e}")
            return {"query": {"match_all": {}}}
    
    async def generate_response_message(
        self,
        user_message: str,
        query_results: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> str:
        """Generate a conversational response based on query results."""
        system_instruction = """
        You are a helpful AI assistant for Elasticsearch data analysis.
        
        Based on the user's question and the query results, provide a clear, 
        conversational response that:
        1. Summarizes what was found
        2. Highlights key insights
        3. Suggests follow-up questions if relevant
        4. Is friendly and professional
        
        Keep responses concise but informative.
        """
        
        prompt = f"""
        User asked: "{user_message}"
        
        Intent: {intent_analysis.get('intent', 'unknown')}
        Query results summary:
        - Total hits: {query_results.get('total_hits', 0)}
        - Has aggregations: {bool(query_results.get('aggregations'))}
        
        Generate a helpful response message.
        """
        
        try:
            response = await self.generate_content(prompt, system_instruction, temperature=0.8)
            return response or "I found some results for your query."
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "I processed your query and found some results."
    
    async def generate_enhanced_chart_recommendations(
        self,
        data: List[Dict[str, Any]],
        intent_analysis: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate enhanced chart recommendations using both AI and ML analysis."""
        try:
            # Get ML-based recommendations
            ml_recommendations = chart_recommendation_service.recommend_charts(
                data=data,
                intent=intent_analysis.get('intent'),
                user_preferences=user_preferences
            )
            
            # Get AI-based analysis for context
            ai_analysis = await self._get_ai_chart_analysis(data, intent_analysis)
            
            # Combine and enhance recommendations
            enhanced_recommendations = []
            
            for ml_rec in ml_recommendations:
                # Generate explanation using AI
                explanation = await self._generate_chart_explanation(ml_rec, data, intent_analysis)
                
                enhanced_rec = {
                    "chart_type": ml_rec.chart_type.value,
                    "confidence": ml_rec.confidence,
                    "reasoning": ml_rec.reasoning,
                    "suggested_fields": ml_rec.suggested_fields,
                    "configuration": ml_rec.configuration,
                    "ai_explanation": explanation,
                    "data_profile": chart_recommendation_service.analyze_data(data).__dict__
                }
                
                enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced chart recommendations: {e}")
            return []
    
    async def _get_ai_chart_analysis(
        self,
        data: List[Dict[str, Any]],
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get AI analysis of data for chart recommendations."""
        if not data:
            return {}
        
        # Sample the data for analysis
        sample_data = data[:5] if len(data) > 5 else data
        
        system_instruction = """
        You are an expert data visualization analyst.
        Analyze the provided data sample and user intent to suggest optimal chart types.
        Consider data characteristics, patterns, and visualization best practices.
        """
        
        prompt = f"""
        Data sample: {json.dumps(sample_data, indent=2)}
        User intent: {intent_analysis.get('intent', 'unknown')}
        Query description: {intent_analysis.get('query_description', '')}
        
        Analyze this data and provide insights for chart selection:
        1. Data characteristics (temporal, categorical, numerical patterns)
        2. Recommended chart types with reasoning
        3. Key insights that should be highlighted
        4. Potential visualization challenges
        
        Return a JSON response with your analysis.
        """
        
        try:
            response = await self.generate_content(prompt, system_instruction, temperature=0.4)
            if response:
                return self._extract_json_from_response(response) or {}
            return {}
        except Exception as e:
            logger.error(f"Failed to get AI chart analysis: {e}")
            return {}
    
    async def _generate_chart_explanation(
        self,
        recommendation: ChartRecommendation,
        data: List[Dict[str, Any]],
        intent_analysis: Dict[str, Any]
    ) -> str:
        """Generate a detailed explanation for a chart recommendation."""
        system_instruction = """
        You are a data visualization expert explaining chart recommendations to users.
        Provide clear, concise explanations that help users understand why a particular
        chart type is recommended for their data and intent.
        """
        
        prompt = f"""
        Chart recommendation:
        - Type: {recommendation.chart_type.value}
        - Confidence: {recommendation.confidence:.1%}
        - Reasoning: {recommendation.reasoning}
        - Suggested fields: {recommendation.suggested_fields}
        
        User intent: {intent_analysis.get('intent', 'unknown')}
        Data size: {len(data)} records
        
        Generate a user-friendly explanation (2-3 sentences) of why this chart type
        is recommended for this specific data and use case.
        """
        
        try:
            response = await self.generate_content(prompt, system_instruction, temperature=0.6)
            return response or recommendation.reasoning
        except Exception as e:
            logger.error(f"Failed to generate chart explanation: {e}")
            return recommendation.reasoning
    
    def _extract_json_from_response(self, response: str) -> Optional[dict]:
        """Extract JSON from Gemini response with multiple strategies."""
        response = response.strip()
        
        # Strategy 1: Look for JSON block markers
        json_markers = ['```json', '```']
        for marker in json_markers:
            if marker in response:
                parts = response.split(marker)
                for part in parts:
                    try:
                        return json.loads(part.strip())
                    except json.JSONDecodeError:
                        continue
        
        # Strategy 2: Find JSON by braces
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Try parsing the entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _validate_intent_analysis(self, data: dict) -> dict:
        """Validate and normalize intent analysis data."""
        valid_intents = ["search", "aggregate", "filter", "chart", "count", "general"]
        valid_chart_types = ["line", "bar", "pie", "scatter", "area"]
        valid_time_ranges = ["last_30_days", "last_week", "today", "last_hour", "last_24_hours"]
        
        # Normalize intent
        intent = data.get("intent", "general").lower()
        if intent not in valid_intents:
            intent = "general"
        
        # Normalize chart type
        chart_type = data.get("chart_type")
        if chart_type and chart_type.lower() not in valid_chart_types:
            chart_type = None
        
        # Normalize time range
        time_range = data.get("time_range")
        if time_range and time_range not in valid_time_ranges:
            time_range = None
        
        return {
            "intent": intent,
            "index": data.get("index"),
            "time_range": time_range,
            "fields": data.get("fields") if isinstance(data.get("fields"), list) else None,
            "chart_type": chart_type,
            "aggregation_type": data.get("aggregation_type"),
            "query_description": data.get("query_description", "User query")
        }
    
    def _get_fallback_intent_analysis(self, description: str) -> dict:
        """Get fallback intent analysis structure."""
        return {
            "intent": "general",
            "index": None,
            "time_range": None,
            "fields": None,
            "chart_type": None,
            "aggregation_type": None,
            "query_description": description
        }


# Note: Service instances are now managed by dependency injection
# See app.core.dependencies for service management 