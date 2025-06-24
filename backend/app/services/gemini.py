import logging
from typing import List, Dict, Any, Optional
import google.genai as genai
from google.genai.types import GenerateContentConfig
import json

from app.core.config import settings
from app.core.exceptions import GeminiAPIError, ConfigurationError

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API using google-genai."""
    
    def __init__(self):
        """Initialize Gemini client."""
        if not settings.google_api_key:
            raise ConfigurationError("GOOGLE_API_KEY not found in environment variables")
        
        try:
            # Configure the client
            genai.configure(api_key=settings.google_api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info("Gemini client initialized successfully")
            
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
                # Prepare the full prompt
                full_prompt = prompt.strip()
                if system_instruction:
                    full_prompt = f"{system_instruction.strip()}\n\nUser: {prompt.strip()}"
                
                # Generate content
                config = GenerateContentConfig(
                    temperature=max(0.0, min(2.0, temperature)),  # Clamp temperature
                    max_output_tokens=max(1, min(8192, max_output_tokens)),  # Clamp tokens
                )
                
                response = await self.client.generate_content_async(
                    contents=full_prompt,
                    config=config
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
                import asyncio
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def analyze_query_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message to determine intent and extract parameters."""
        system_instruction = """
        You are an expert at analyzing user queries for Elasticsearch operations.
        
        Given a user message, identify:
        1. Intent: search, aggregate, filter, chart, count, or general
        2. Index: which elasticsearch index to query (if mentioned)
        3. Time range: any time-based filters
        4. Fields: relevant fields mentioned
        5. Chart type: if user wants visualization (line, bar, pie)
        6. Aggregation: type of aggregation needed (terms, date_histogram, avg, sum, etc.)
        
        Respond with a JSON object containing these fields.
        If uncertain, make reasonable assumptions or mark as null.
        
        Available sample indices: sample-sales, sample-logs
        """
        
        prompt = f"""
        User message: "{user_message}"
        
        Analyze this message and return a JSON response with:
        {{
            "intent": "search|aggregate|filter|chart|count|general",
            "index": "index_name or null",
            "time_range": "last_30_days|last_week|today|null",
            "fields": ["field1", "field2"] or null,
            "chart_type": "line|bar|pie|null",
            "aggregation_type": "terms|date_histogram|avg|sum|count|null",
            "query_description": "brief description of what user wants"
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