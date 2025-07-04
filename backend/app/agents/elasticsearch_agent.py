import logging
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from app.services.gemini import GeminiService
from app.services.elasticsearch import ElasticsearchService
from app.services.redis import RedisService
from app.services.vector_db import VectorDBService
from app.services.query_intelligence import query_intelligence_service, QueryInsight
import hashlib
import json

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the Elasticsearch Agent."""
    user_message: str
    session_id: str
    intent_analysis: Optional[Dict[str, Any]]
    elasticsearch_query: Optional[Dict[str, Any]]
    query_results: Optional[Dict[str, Any]]
    response_message: str
    chart_config: Optional[Dict[str, Any]]
    available_indices: List[str]
    error: Optional[str]
    query_insight: Optional[QueryInsight]
    personalized_suggestions: Optional[List[str]]


class ElasticsearchAgent:
    """LangGraph agent for Elasticsearch data analysis and visualization."""
    
    def __init__(
        self,
        gemini_service: GeminiService = None,
        elasticsearch_service: ElasticsearchService = None,
        redis_service: RedisService = None,
        vector_db_service: VectorDBService = None
    ):
        """Initialize the agent with workflow graph and services."""
        # Store service instances
        self.gemini_service = gemini_service
        self.elasticsearch_service = elasticsearch_service
        self.redis_service = redis_service
        self.vector_db_service = vector_db_service
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("get_indices", self._get_available_indices)
        workflow.add_node("analyze_intelligence", self._analyze_query_intelligence)
        workflow.add_node("generate_query", self._generate_elasticsearch_query)
        workflow.add_node("execute_query", self._execute_query)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("error_handler", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("get_indices")
        
        # Add edges
        workflow.add_edge("get_indices", "analyze_intent")
        workflow.add_edge("analyze_intent", "analyze_intelligence")
        workflow.add_conditional_edges(
            "analyze_intelligence",
            self._should_query_elasticsearch,
            {
                "query": "generate_query",
                "skip": "generate_response"
            }
        )
        workflow.add_edge("generate_query", "execute_query")
        workflow.add_edge("execute_query", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def _get_available_indices(self, state: AgentState) -> AgentState:
        """Get available Elasticsearch indices."""
        try:
            indices = await self.elasticsearch_service.list_indices()
            state["available_indices"] = indices
            logger.info(f"Found {len(indices)} available indices")
            
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            state["available_indices"] = []
            state["error"] = "Failed to connect to Elasticsearch"
        
        return state
    
    async def _analyze_intent(self, state: AgentState) -> AgentState:
        """Analyze user intent using Gemini with semantic search enhancement."""
        try:
            user_message = state["user_message"]
            session_id = state.get("session_id")
            
            # First, try to find similar queries using vector search
            similar_queries = []
            if self.vector_db_service:
                try:
                    similar_queries = await self.vector_db_service.find_similar_queries(
                        user_message, limit=3, similarity_threshold=0.7
                    )
                    logger.info(f"Found {len(similar_queries)} similar queries")
                except Exception as e:
                    logger.warning(f"Vector search failed: {e}")
            
            # Get conversation context if available
            conversation_context = []
            if self.vector_db_service and session_id:
                try:
                    conversation_context = await self.vector_db_service.get_conversation_context(
                        session_id, user_message, limit=3
                    )
                    logger.info(f"Found {len(conversation_context)} context items")
                except Exception as e:
                    logger.warning(f"Context retrieval failed: {e}")
            
            # Enhanced intent analysis with context
            intent_analysis = await self.gemini_service.analyze_query_intent(
                user_message,
                similar_queries=similar_queries,
                conversation_context=conversation_context
            )
            
            state["intent_analysis"] = intent_analysis
            state["similar_queries"] = similar_queries
            state["conversation_context"] = conversation_context
            logger.info(f"Enhanced intent analyzed: {intent_analysis.get('intent', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            state["intent_analysis"] = {
                "intent": "general",
                "query_description": "Failed to analyze intent"
            }
            state["similar_queries"] = []
            state["conversation_context"] = []
            state["error"] = "Failed to analyze your request"
        
        return state
    
    async def _analyze_query_intelligence(self, state: AgentState) -> AgentState:
        """Analyze query intelligence patterns and user behavior."""
        try:
            user_message = state["user_message"]
            session_id = state.get("session_id")
            intent_analysis = state.get("intent_analysis", {})
            
            # Initialize query intelligence service with our services
            query_intelligence_service.vector_db_service = self.vector_db_service
            query_intelligence_service.redis_service = self.redis_service
            
            # Analyze query patterns
            query_insight = await query_intelligence_service.analyze_query_pattern(
                user_message=user_message,
                intent_analysis=intent_analysis,
                session_id=session_id
            )
            
            state["query_insight"] = query_insight
            
            # Get personalized suggestions
            if session_id:
                suggestions = await query_intelligence_service.get_personalized_suggestions(
                    session_id=session_id,
                    current_context=user_message
                )
                state["personalized_suggestions"] = suggestions
            
            logger.info(f"Query intelligence analysis completed: {query_insight.pattern.value} "
                       f"(confidence: {query_insight.confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Query intelligence analysis failed: {e}")
            # Continue without intelligence analysis
            state["query_insight"] = None
            state["personalized_suggestions"] = []
        
        return state
    
    def _should_query_elasticsearch(self, state: AgentState) -> str:
        """Determine if we should query Elasticsearch or skip."""
        if state.get("error"):
            return "skip"
        
        intent = state.get("intent_analysis", {}).get("intent", "general")
        
        # Query ES for data-related intents
        if intent in ["search", "aggregate", "filter", "chart", "count"]:
            return "query"
        else:
            return "skip"
    
    async def _generate_elasticsearch_query(self, state: AgentState) -> AgentState:
        """Generate Elasticsearch query using Gemini."""
        try:
            intent_analysis = state.get("intent_analysis", {})
            available_indices = state.get("available_indices", [])
            
            # Check cache first
            query_hash = self._generate_query_hash(state["user_message"], intent_analysis)
            cached_query = await self.redis_service.get_cached_query(query_hash)
            
            if cached_query:
                logger.info("Using cached query")
                state["elasticsearch_query"] = cached_query
            else:
                # Generate new query
                es_query = await self.gemini_service.generate_elasticsearch_query(
                    intent_analysis, available_indices
                )
                
                state["elasticsearch_query"] = es_query
                
                # Cache the query
                await self.redis_service.cache_query_result(query_hash, es_query, expire=3600)
                
            logger.info("Elasticsearch query generated")
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            state["elasticsearch_query"] = {"query": {"match_all": {}}}
            state["error"] = "Failed to generate query"
        
        return state
    
    async def _execute_query(self, state: AgentState) -> AgentState:
        """Execute the Elasticsearch query with enhanced error handling."""
        try:
            intent_analysis = state.get("intent_analysis", {})
            es_query = state.get("elasticsearch_query", {})
            
            # Determine target index with better fallback logic
            target_index = self._determine_target_index(intent_analysis, state["available_indices"])
            if not target_index:
                state["error"] = "No suitable Elasticsearch index found"
                state["query_results"] = {"total_hits": 0, "data": [], "aggregations": {}}
                return state
            
            # Execute query with size limits
            query_size = min(intent_analysis.get("size", 10), 100)  # Limit to 100 results
            
            query_results = await self.elasticsearch_service.simple_search(
                index=target_index,
                query=es_query,
                size=query_size
            )
            
            # Check for errors in query results
            if query_results.get("error"):
                state["error"] = query_results["error"]
                state["query_results"] = {"total_hits": 0, "data": [], "aggregations": {}}
                return state
            
            state["query_results"] = query_results
            
            # Generate enhanced chart config if needed and data is available
            if query_results.get("total_hits", 0) > 0:
                chart_config = await self._generate_enhanced_chart_config(
                    intent_analysis, query_results
                )
                state["chart_config"] = chart_config
            
            logger.info(f"Query executed successfully on '{target_index}': {query_results['total_hits']} hits")
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            state["query_results"] = {"total_hits": 0, "data": [], "aggregations": {}}
            state["error"] = f"Failed to execute query: {str(e)}"
        
        return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate conversational response using Gemini and store successful queries."""
        try:
            user_message = state["user_message"]
            session_id = state.get("session_id")
            intent_analysis = state.get("intent_analysis", {})
            query_results = state.get("query_results", {})
            query_insight = state.get("query_insight")
            suggestions = state.get("personalized_suggestions", [])
            
            if state.get("error"):
                # Generate error response
                state["response_message"] = f"I apologize, but I encountered an issue: {state['error']}. Please try rephrasing your question."
            else:
                # Generate enhanced response with intelligence insights
                base_response = await self.gemini_service.generate_response_message(
                    user_message, query_results, intent_analysis
                )
                
                # Enhance response with intelligence insights
                enhanced_response = self._enhance_response_with_intelligence(
                    base_response, query_insight, suggestions
                )
                
                state["response_message"] = enhanced_response
                
                # Store successful query in vector database for future semantic search
                if self.vector_db_service and query_results.get("total_hits", 0) > 0:
                    try:
                        elasticsearch_query = state.get("elasticsearch_query", {})
                        await self.vector_db_service.store_query_example(
                            natural_query=user_message,
                            elasticsearch_query=elasticsearch_query,
                            intent=intent_analysis.get("intent", "general"),
                            index_name=self._determine_target_index(intent_analysis, state["available_indices"]) or "unknown",
                            result_count=query_results.get("total_hits", 0),
                            metadata={
                                "chart_type": intent_analysis.get("chart_type"),
                                "aggregation_type": intent_analysis.get("aggregation_type"),
                                "session_id": session_id
                            }
                        )
                        logger.info("Stored successful query in vector database")
                    except Exception as e:
                        logger.warning(f"Failed to store query in vector database: {e}")
            
            # Store conversation context regardless of success/error
            if self.vector_db_service and session_id:
                try:
                    await self.vector_db_service.store_conversation_context(
                        session_id=session_id,
                        user_message=user_message,
                        agent_response=state["response_message"],
                        intent=intent_analysis.get("intent", "general"),
                        query_result=query_results
                    )
                    logger.info("Stored conversation context")
                except Exception as e:
                    logger.warning(f"Failed to store conversation context: {e}")
            
            # Update user profile with query insights
            if query_insight and session_id:
                try:
                    await query_intelligence_service.update_user_profile(
                        session_id=session_id,
                        query_insight=query_insight,
                        intent_analysis=intent_analysis,
                        user_feedback=None  # Could be collected from frontend
                    )
                    logger.info("Updated user profile with query insights")
                except Exception as e:
                    logger.warning(f"Failed to update user profile: {e}")
            
            logger.info("Response generated successfully")
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            state["response_message"] = "I processed your request, but had trouble generating a response."
        
        return state
    
    async def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors in the workflow."""
        error_msg = state.get("error", "An unknown error occurred")
        state["response_message"] = f"I apologize, but I encountered an issue: {error_msg}"
        return state
    
    def _determine_target_index(self, intent_analysis: Dict[str, Any], available_indices: List[str]) -> Optional[str]:
        """Determine the best target index for the query."""
        if not available_indices:
            return None
        
        # Check if user specified an index
        specified_index = intent_analysis.get("index")
        if specified_index and specified_index in available_indices:
            return specified_index
        
        # Smart index selection based on intent
        intent = intent_analysis.get("intent", "general")
        
        # Prefer sample indices for demos
        if "sample-sales" in available_indices and intent in ["chart", "aggregate", "search"]:
            return "sample-sales"
        elif "sample-logs" in available_indices and intent in ["search", "filter"]:
            return "sample-logs"
        
        # Filter out system indices (starting with .)
        user_indices = [idx for idx in available_indices if not idx.startswith('.')]
        
        if user_indices:
            return user_indices[0]  # Return first non-system index
        
        return available_indices[0] if available_indices else None
    
    def _generate_query_hash(self, user_message: str, intent_analysis: Dict[str, Any]) -> str:
        """Generate hash for caching queries."""
        cache_key = f"{user_message}_{json.dumps(intent_analysis, sort_keys=True)}"
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    def _generate_chart_config(
        self, 
        intent_analysis: Dict[str, Any], 
        query_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced chart configuration based on data and intent."""
        chart_type = intent_analysis.get("chart_type", "bar")
        data = query_results.get("data", [])
        aggregations = query_results.get("aggregations", {})
        
        # Basic config
        config = {
            "chart_type": chart_type,
            "title": intent_analysis.get("query_description", "Data Visualization"),
            "has_data": len(data) > 0,
            "data_count": len(data)
        }
        
        # If we have aggregations, use them for chart data
        if aggregations:
            config["use_aggregations"] = True
            config["aggregation_data"] = aggregations
        else:
            config["use_aggregations"] = False
            
        # Suggest fields for axes based on data structure
        if data and len(data) > 0:
            sample_doc = data[0]
            numeric_fields = []
            text_fields = []
            date_fields = []
            
            for field, value in sample_doc.items():
                if isinstance(value, (int, float)):
                    numeric_fields.append(field)
                elif isinstance(value, str):
                    if "timestamp" in field.lower() or "date" in field.lower():
                        date_fields.append(field)
                    else:
                        text_fields.append(field)
            
            config["suggested_fields"] = {
                "numeric": numeric_fields[:3],  # Limit suggestions
                "text": text_fields[:3],
                "date": date_fields[:3]
            }
            
            # Smart axis suggestions based on chart type
            if chart_type == "line" and date_fields:
                config["x_axis_suggestion"] = date_fields[0]
                config["y_axis_suggestion"] = numeric_fields[0] if numeric_fields else None
            elif chart_type == "bar" and text_fields:
                config["x_axis_suggestion"] = text_fields[0]
                config["y_axis_suggestion"] = numeric_fields[0] if numeric_fields else None
            elif chart_type == "pie" and text_fields:
                config["label_field"] = text_fields[0]
                config["value_field"] = numeric_fields[0] if numeric_fields else None
        
        return config
    
    async def _generate_enhanced_chart_config(
        self, 
        intent_analysis: Dict[str, Any], 
        query_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced chart configuration using AI and ML recommendations."""
        try:
            data = query_results.get("data", [])
            if not data:
                return self._generate_chart_config(intent_analysis, query_results)
            
            # Get enhanced chart recommendations from Gemini service
            enhanced_recommendations = await self.gemini_service.generate_enhanced_chart_recommendations(
                data=data,
                intent_analysis=intent_analysis,
                user_preferences=None  # Could be retrieved from user profile in the future
            )
            
            # Use the top recommendation or fallback to basic config
            if enhanced_recommendations:
                top_recommendation = enhanced_recommendations[0]
                
                # Build enhanced config
                config = {
                    "chart_type": top_recommendation["chart_type"],
                    "title": intent_analysis.get("query_description", "Data Visualization"),
                    "has_data": len(data) > 0,
                    "data_count": len(data),
                    "confidence": top_recommendation["confidence"],
                    "reasoning": top_recommendation["reasoning"],
                    "ai_explanation": top_recommendation.get("ai_explanation", ""),
                    "suggested_fields": top_recommendation["suggested_fields"],
                    "configuration": top_recommendation["configuration"],
                    "alternative_charts": [
                        {
                            "type": rec["chart_type"],
                            "confidence": rec["confidence"],
                            "reasoning": rec["reasoning"]
                        }
                        for rec in enhanced_recommendations[1:3]  # Include top 2 alternatives
                    ],
                    "data_profile": top_recommendation.get("data_profile", {})
                }
                
                # Add aggregation handling
                aggregations = query_results.get("aggregations", {})
                if aggregations:
                    config["use_aggregations"] = True
                    config["aggregation_data"] = aggregations
                else:
                    config["use_aggregations"] = False
                
                # Add smart field mapping based on ML recommendations
                if data and len(data) > 0:
                    sample_doc = data[0]
                    
                    # Extract field types for better mapping
                    numeric_fields = []
                    text_fields = []
                    date_fields = []
                    
                    for field, value in sample_doc.items():
                        if isinstance(value, (int, float)):
                            numeric_fields.append(field)
                        elif isinstance(value, str):
                            if "timestamp" in field.lower() or "date" in field.lower():
                                date_fields.append(field)
                            else:
                                text_fields.append(field)
                    
                    config["available_fields"] = {
                        "numeric": numeric_fields,
                        "text": text_fields,
                        "date": date_fields
                    }
                    
                    # Smart axis suggestions based on ML recommendations and chart type
                    chart_type = config["chart_type"]
                    suggested_fields = config["suggested_fields"]
                    
                    if chart_type in ["line", "area"] and date_fields:
                        config["x_axis_suggestion"] = suggested_fields.get("x_axis", date_fields[0])
                        config["y_axis_suggestion"] = suggested_fields.get("y_axis", numeric_fields[0] if numeric_fields else None)
                    elif chart_type == "bar" and text_fields:
                        config["x_axis_suggestion"] = suggested_fields.get("x_axis", text_fields[0])
                        config["y_axis_suggestion"] = suggested_fields.get("y_axis", numeric_fields[0] if numeric_fields else None)
                    elif chart_type == "pie" and text_fields:
                        config["label_field"] = suggested_fields.get("label", text_fields[0])
                        config["value_field"] = suggested_fields.get("value", numeric_fields[0] if numeric_fields else None)
                    elif chart_type == "scatter" and len(numeric_fields) >= 2:
                        config["x_axis_suggestion"] = suggested_fields.get("x_axis", numeric_fields[0])
                        config["y_axis_suggestion"] = suggested_fields.get("y_axis", numeric_fields[1])
                
                logger.info(f"Generated enhanced chart config: {chart_type} with {config['confidence']:.1%} confidence")
                return config
            
            # Fallback to basic config if enhanced recommendations fail
            logger.warning("Enhanced chart recommendations failed, using basic config")
            return self._generate_chart_config(intent_analysis, query_results)
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced chart config: {e}")
            # Fallback to basic chart config
            return self._generate_chart_config(intent_analysis, query_results)
    
    def _enhance_response_with_intelligence(
        self,
        base_response: str,
        query_insight: Optional[QueryInsight],
        suggestions: List[str]
    ) -> str:
        """Enhance response with intelligence insights and suggestions."""
        
        enhanced_response = base_response
        
        # Add query pattern insights
        if query_insight and query_insight.confidence > 0.7:
            pattern_name = query_insight.pattern.value.replace('_', ' ').title()
            enhanced_response += f"\n\n🧠 **Intelligence Insight**: I detected a {pattern_name} pattern in your query "
            enhanced_response += f"(confidence: {query_insight.confidence:.0%}). {query_insight.reasoning}"
            
            # Add improvement suggestions
            if query_insight.suggested_improvements:
                enhanced_response += "\n\n💡 **Suggestions for better analysis**:"
                for i, improvement in enumerate(query_insight.suggested_improvements[:3], 1):
                    enhanced_response += f"\n{i}. {improvement}"
        
        # Add personalized suggestions
        if suggestions:
            enhanced_response += "\n\n🎯 **You might also want to try**:"
            for i, suggestion in enumerate(suggestions[:3], 1):
                enhanced_response += f"\n{i}. {suggestion}"
        
        return enhanced_response
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Process user message through the agent workflow."""
        initial_state: AgentState = {
            "user_message": user_message,
            "session_id": session_id,
            "intent_analysis": None,
            "elasticsearch_query": None,
            "query_results": None,
            "response_message": "",
            "chart_config": None,
            "available_indices": [],
            "error": None,
            "query_insight": None,
            "personalized_suggestions": []
        }
        
        try:
            # Run the workflow
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "response": result["response_message"],
                "session_id": session_id,
                "chart_config": result.get("chart_config"),
                "data": result.get("query_results", {}).get("data", []),
                "intent": result.get("intent_analysis", {}).get("intent", "general"),
                "query_insight": result.get("query_insight"),
                "personalized_suggestions": result.get("personalized_suggestions", []),
                "intelligence_metrics": {
                    "pattern": result.get("query_insight").pattern.value if result.get("query_insight") else None,
                    "confidence": result.get("query_insight").confidence if result.get("query_insight") else None,
                    "user_behavior": result.get("query_insight").user_behavior_hint.value if result.get("query_insight") and result.get("query_insight").user_behavior_hint else None
                }
            }
            
        except Exception as e:
            logger.error(f"Agent workflow failed: {e}")
            return {
                "response": "I apologize, but I encountered an unexpected error while processing your request.",
                "session_id": session_id,
                "chart_config": None,
                "data": [],
                "intent": "error"
            }


# Note: Agent instances are now managed by dependency injection
# See app.core.dependencies for agent management 