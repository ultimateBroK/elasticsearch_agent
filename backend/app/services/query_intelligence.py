"""Advanced query intelligence service for pattern recognition and learning."""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QueryPattern(Enum):
    """Types of query patterns we can recognize."""
    TIME_SERIES_ANALYSIS = "time_series_analysis"
    CATEGORICAL_COMPARISON = "categorical_comparison"
    AGGREGATION_SUMMARY = "aggregation_summary"
    CORRELATION_ANALYSIS = "correlation_analysis"
    DISTRIBUTION_ANALYSIS = "distribution_analysis"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    DRILL_DOWN = "drill_down"
    ROLL_UP = "roll_up"
    FILTER_REFINEMENT = "filter_refinement"


class UserBehavior(Enum):
    """User behavior patterns."""
    EXPLORER = "explorer"  # Tries many different queries
    ANALYST = "analyst"    # Deep dives into specific areas
    REPORTER = "reporter"  # Focuses on standard reports
    CASUAL = "casual"      # Occasional simple queries


@dataclass
class QueryInsight:
    """Insights derived from query analysis."""
    pattern: QueryPattern
    confidence: float
    reasoning: str
    suggested_improvements: List[str]
    related_patterns: List[QueryPattern]
    user_behavior_hint: Optional[UserBehavior]


@dataclass
class UserProfile:
    """User behavior profile based on query history."""
    session_id: str
    behavior_type: UserBehavior
    preferred_chart_types: List[str]
    common_fields: List[str]
    query_complexity: float  # 0.0 to 1.0
    domain_expertise: Dict[str, float]  # field -> expertise level
    interaction_patterns: Dict[str, int]
    last_updated: datetime


class QueryIntelligenceService:
    """Advanced query intelligence and pattern recognition service."""
    
    def __init__(self, vector_db_service=None, redis_service=None):
        """Initialize the query intelligence service."""
        self.vector_db_service = vector_db_service
        self.redis_service = redis_service
        self.pattern_rules = self._build_pattern_rules()
        self.user_profiles = {}  # In-memory cache, could be persisted
        
    def _build_pattern_rules(self) -> Dict[QueryPattern, Dict[str, Any]]:
        """Build pattern recognition rules."""
        return {
            QueryPattern.TIME_SERIES_ANALYSIS: {
                "keywords": ["over time", "timeline", "trend", "progression", "daily", "monthly", "yearly"],
                "field_types": ["temporal", "date", "timestamp"],
                "chart_types": ["line", "area"],
                "complexity": 0.6,
                "confidence_boost": 0.3
            },
            
            QueryPattern.CATEGORICAL_COMPARISON: {
                "keywords": ["compare", "versus", "vs", "between", "across", "by category"],
                "field_types": ["categorical", "text"],
                "chart_types": ["bar", "pie"],
                "complexity": 0.4,
                "confidence_boost": 0.2
            },
            
            QueryPattern.AGGREGATION_SUMMARY: {
                "keywords": ["total", "sum", "average", "count", "max", "min", "summary"],
                "aggregation_types": ["sum", "avg", "count", "max", "min"],
                "chart_types": ["bar", "pie"],
                "complexity": 0.3,
                "confidence_boost": 0.4
            },
            
            QueryPattern.CORRELATION_ANALYSIS: {
                "keywords": ["correlation", "relationship", "association", "related", "impact"],
                "field_types": ["numeric"],
                "chart_types": ["scatter", "heatmap"],
                "complexity": 0.8,
                "confidence_boost": 0.5
            },
            
            QueryPattern.DISTRIBUTION_ANALYSIS: {
                "keywords": ["distribution", "spread", "range", "histogram", "frequency"],
                "field_types": ["numeric"],
                "chart_types": ["histogram", "box"],
                "complexity": 0.7,
                "confidence_boost": 0.4
            },
            
            QueryPattern.TREND_ANALYSIS: {
                "keywords": ["trend", "pattern", "growth", "decline", "increase", "decrease"],
                "field_types": ["temporal", "numeric"],
                "chart_types": ["line", "area"],
                "complexity": 0.6,
                "confidence_boost": 0.3
            },
            
            QueryPattern.ANOMALY_DETECTION: {
                "keywords": ["anomaly", "outlier", "unusual", "abnormal", "spike", "drop"],
                "field_types": ["numeric"],
                "chart_types": ["line", "scatter"],
                "complexity": 0.9,
                "confidence_boost": 0.6
            },
            
            QueryPattern.DRILL_DOWN: {
                "keywords": ["detail", "breakdown", "drill down", "specific", "individual"],
                "complexity": 0.5,
                "confidence_boost": 0.2
            },
            
            QueryPattern.ROLL_UP: {
                "keywords": ["overview", "summary", "high level", "aggregate", "total"],
                "complexity": 0.3,
                "confidence_boost": 0.2
            },
            
            QueryPattern.FILTER_REFINEMENT: {
                "keywords": ["filter", "where", "only", "exclude", "include", "specific"],
                "complexity": 0.4,
                "confidence_boost": 0.1
            }
        }
    
    async def analyze_query_pattern(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any],
        query_results: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> QueryInsight:
        """Analyze query to identify patterns and provide insights."""
        
        try:
            # Identify the primary pattern
            pattern, confidence = self._identify_primary_pattern(user_message, intent_analysis)
            
            # Generate reasoning
            reasoning = self._generate_pattern_reasoning(pattern, user_message, intent_analysis)
            
            # Suggest improvements
            improvements = await self._suggest_query_improvements(
                pattern, user_message, intent_analysis, query_results
            )
            
            # Find related patterns
            related_patterns = self._find_related_patterns(pattern, intent_analysis)
            
            # Analyze user behavior
            user_behavior = await self._analyze_user_behavior(session_id, pattern, intent_analysis)
            
            return QueryInsight(
                pattern=pattern,
                confidence=confidence,
                reasoning=reasoning,
                suggested_improvements=improvements,
                related_patterns=related_patterns,
                user_behavior_hint=user_behavior
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze query pattern: {e}")
            return QueryInsight(
                pattern=QueryPattern.CATEGORICAL_COMPARISON,
                confidence=0.5,
                reasoning="Default pattern analysis",
                suggested_improvements=[],
                related_patterns=[],
                user_behavior_hint=None
            )
    
    def _identify_primary_pattern(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any]
    ) -> Tuple[QueryPattern, float]:
        """Identify the primary query pattern."""
        
        message_lower = user_message.lower()
        pattern_scores = {}
        
        for pattern, rules in self.pattern_rules.items():
            score = 0.0
            
            # Keyword matching
            keywords = rules.get("keywords", [])
            keyword_matches = sum(1 for keyword in keywords if keyword in message_lower)
            if keywords:
                score += (keyword_matches / len(keywords)) * 0.4
            
            # Field type matching
            field_types = rules.get("field_types", [])
            intent_fields = intent_analysis.get("fields", [])
            if field_types and intent_fields:
                # This is simplified - in practice, you'd analyze actual field types
                field_match = any(ft in str(intent_fields).lower() for ft in field_types)
                if field_match:
                    score += 0.3
            
            # Chart type matching
            chart_types = rules.get("chart_types", [])
            intent_chart = intent_analysis.get("chart_type")
            if chart_types and intent_chart and intent_chart in chart_types:
                score += 0.2
            
            # Aggregation type matching
            agg_types = rules.get("aggregation_types", [])
            intent_agg = intent_analysis.get("aggregation_type")
            if agg_types and intent_agg and intent_agg in agg_types:
                score += 0.1
            
            # Apply confidence boost
            if score > 0:
                score += rules.get("confidence_boost", 0.0)
            
            pattern_scores[pattern] = min(1.0, score)
        
        # Find the highest scoring pattern
        if pattern_scores:
            best_pattern = max(pattern_scores, key=pattern_scores.get)
            confidence = pattern_scores[best_pattern]
            return best_pattern, confidence
        
        # Default fallback
        return QueryPattern.CATEGORICAL_COMPARISON, 0.5
    
    def _generate_pattern_reasoning(
        self,
        pattern: QueryPattern,
        user_message: str,
        intent_analysis: Dict[str, Any]
    ) -> str:
        """Generate reasoning for the identified pattern."""
        
        reasoning_templates = {
            QueryPattern.TIME_SERIES_ANALYSIS: "Detected time-based analysis pattern with temporal data focus",
            QueryPattern.CATEGORICAL_COMPARISON: "Identified categorical comparison pattern for data segmentation",
            QueryPattern.AGGREGATION_SUMMARY: "Recognized aggregation pattern for data summarization",
            QueryPattern.CORRELATION_ANALYSIS: "Found correlation analysis pattern for relationship exploration",
            QueryPattern.DISTRIBUTION_ANALYSIS: "Detected distribution analysis pattern for data spread examination",
            QueryPattern.TREND_ANALYSIS: "Identified trend analysis pattern for pattern recognition",
            QueryPattern.ANOMALY_DETECTION: "Recognized anomaly detection pattern for outlier identification",
            QueryPattern.DRILL_DOWN: "Detected drill-down pattern for detailed exploration",
            QueryPattern.ROLL_UP: "Identified roll-up pattern for high-level overview",
            QueryPattern.FILTER_REFINEMENT: "Found filter refinement pattern for data subset analysis"
        }
        
        base_reasoning = reasoning_templates.get(pattern, "Pattern analysis completed")
        
        # Add context-specific details
        intent = intent_analysis.get("intent", "unknown")
        chart_type = intent_analysis.get("chart_type")
        
        if chart_type:
            base_reasoning += f" with {chart_type} visualization preference"
        
        if intent != "unknown":
            base_reasoning += f" (intent: {intent})"
        
        return base_reasoning
    
    async def _suggest_query_improvements(
        self,
        pattern: QueryPattern,
        user_message: str,
        intent_analysis: Dict[str, Any],
        query_results: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Suggest improvements based on pattern analysis."""
        
        improvements = []
        
        # Pattern-specific suggestions
        if pattern == QueryPattern.TIME_SERIES_ANALYSIS:
            improvements.extend([
                "Consider adding time range filters for focused analysis",
                "Try grouping by different time intervals (daily, weekly, monthly)",
                "Add trend lines or moving averages for clearer patterns"
            ])
        
        elif pattern == QueryPattern.CATEGORICAL_COMPARISON:
            improvements.extend([
                "Consider limiting categories for clearer visualization",
                "Try sorting by values for better readability",
                "Add percentage calculations for relative comparisons"
            ])
        
        elif pattern == QueryPattern.CORRELATION_ANALYSIS:
            improvements.extend([
                "Include correlation coefficients in the analysis",
                "Consider scatter plot with trend lines",
                "Filter outliers for clearer correlation patterns"
            ])
        
        elif pattern == QueryPattern.AGGREGATION_SUMMARY:
            improvements.extend([
                "Add breakdown by key dimensions",
                "Include percentage of total calculations",
                "Consider multiple aggregation metrics"
            ])
        
        # Result-based suggestions
        if query_results:
            total_hits = query_results.get("total_hits", 0)
            
            if total_hits == 0:
                improvements.append("Try broadening your search criteria")
            elif total_hits > 1000:
                improvements.append("Consider adding filters to narrow down results")
            elif total_hits < 10:
                improvements.append("Try expanding your search criteria for more comprehensive analysis")
        
        # Intent-based suggestions
        intent = intent_analysis.get("intent")
        if intent == "chart" and not intent_analysis.get("chart_type"):
            improvements.append("Specify a preferred chart type for better visualization")
        
        return improvements[:3]  # Limit to top 3 suggestions
    
    def _find_related_patterns(
        self,
        primary_pattern: QueryPattern,
        intent_analysis: Dict[str, Any]
    ) -> List[QueryPattern]:
        """Find patterns related to the primary pattern."""
        
        related_patterns_map = {
            QueryPattern.TIME_SERIES_ANALYSIS: [
                QueryPattern.TREND_ANALYSIS,
                QueryPattern.ANOMALY_DETECTION
            ],
            QueryPattern.CATEGORICAL_COMPARISON: [
                QueryPattern.AGGREGATION_SUMMARY,
                QueryPattern.DRILL_DOWN
            ],
            QueryPattern.CORRELATION_ANALYSIS: [
                QueryPattern.DISTRIBUTION_ANALYSIS,
                QueryPattern.ANOMALY_DETECTION
            ],
            QueryPattern.TREND_ANALYSIS: [
                QueryPattern.TIME_SERIES_ANALYSIS,
                QueryPattern.ANOMALY_DETECTION
            ],
            QueryPattern.DRILL_DOWN: [
                QueryPattern.FILTER_REFINEMENT,
                QueryPattern.CATEGORICAL_COMPARISON
            ],
            QueryPattern.ROLL_UP: [
                QueryPattern.AGGREGATION_SUMMARY,
                QueryPattern.CATEGORICAL_COMPARISON
            ]
        }
        
        return related_patterns_map.get(primary_pattern, [])
    
    async def _analyze_user_behavior(
        self,
        session_id: Optional[str],
        current_pattern: QueryPattern,
        intent_analysis: Dict[str, Any]
    ) -> Optional[UserBehavior]:
        """Analyze user behavior based on query history."""
        
        if not session_id or not self.vector_db_service:
            return None
        
        try:
            # Get conversation context
            context = await self.vector_db_service.get_conversation_context(
                session_id, "", limit=10
            )
            
            if not context:
                return UserBehavior.CASUAL
            
            # Analyze patterns
            query_count = len(context)
            unique_intents = set(ctx.get("intent", "unknown") for ctx in context)
            
            # Determine behavior type
            if query_count >= 10:
                if len(unique_intents) > 5:
                    return UserBehavior.EXPLORER
                else:
                    return UserBehavior.ANALYST
            elif query_count >= 5:
                return UserBehavior.REPORTER
            else:
                return UserBehavior.CASUAL
                
        except Exception as e:
            logger.error(f"Failed to analyze user behavior: {e}")
            return None
    
    async def update_user_profile(
        self,
        session_id: str,
        query_insight: QueryInsight,
        intent_analysis: Dict[str, Any],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """Update user profile based on query insights and feedback."""
        
        # Get or create user profile
        profile = self.user_profiles.get(session_id)
        if not profile:
            profile = UserProfile(
                session_id=session_id,
                behavior_type=UserBehavior.CASUAL,
                preferred_chart_types=[],
                common_fields=[],
                query_complexity=0.5,
                domain_expertise={},
                interaction_patterns={},
                last_updated=datetime.now()
            )
        
        # Update behavior type
        if query_insight.user_behavior_hint:
            profile.behavior_type = query_insight.user_behavior_hint
        
        # Update preferred chart types
        chart_type = intent_analysis.get("chart_type")
        if chart_type and chart_type not in profile.preferred_chart_types:
            profile.preferred_chart_types.append(chart_type)
            # Keep only top 5 preferences
            profile.preferred_chart_types = profile.preferred_chart_types[-5:]
        
        # Update common fields
        fields = intent_analysis.get("fields", [])
        for field in fields:
            if field not in profile.common_fields:
                profile.common_fields.append(field)
        profile.common_fields = profile.common_fields[-10:]  # Keep recent fields
        
        # Update query complexity (moving average)
        pattern_complexity = self.pattern_rules.get(query_insight.pattern, {}).get("complexity", 0.5)
        profile.query_complexity = (profile.query_complexity * 0.8) + (pattern_complexity * 0.2)
        
        # Update interaction patterns
        pattern_name = query_insight.pattern.value
        profile.interaction_patterns[pattern_name] = profile.interaction_patterns.get(pattern_name, 0) + 1
        
        # Update domain expertise based on successful queries
        if user_feedback and user_feedback.get("satisfaction", 0) > 0.7:
            index_name = intent_analysis.get("index", "general")
            current_expertise = profile.domain_expertise.get(index_name, 0.0)
            profile.domain_expertise[index_name] = min(1.0, current_expertise + 0.1)
        
        profile.last_updated = datetime.now()
        self.user_profiles[session_id] = profile
        
        return profile
    
    async def get_personalized_suggestions(
        self,
        session_id: str,
        current_context: Optional[str] = None
    ) -> List[str]:
        """Get personalized query suggestions based on user profile."""
        
        profile = self.user_profiles.get(session_id)
        if not profile:
            return self._get_default_suggestions()
        
        suggestions = []
        
        # Behavior-based suggestions
        if profile.behavior_type == UserBehavior.EXPLORER:
            suggestions.extend([
                "Try exploring correlations between different fields",
                "Experiment with different chart types for the same data",
                "Look for anomalies or outliers in your data"
            ])
        elif profile.behavior_type == UserBehavior.ANALYST:
            suggestions.extend([
                "Drill down into specific segments for deeper insights",
                "Compare trends across different time periods",
                "Analyze distribution patterns in your data"
            ])
        elif profile.behavior_type == UserBehavior.REPORTER:
            suggestions.extend([
                "Create summary reports with key metrics",
                "Generate comparative analysis across categories",
                "Build time-series reports for trend tracking"
            ])
        
        # Pattern-based suggestions
        common_patterns = sorted(
            profile.interaction_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for pattern_name, _ in common_patterns:
            if pattern_name == QueryPattern.TIME_SERIES_ANALYSIS.value:
                suggestions.append("Analyze trends over different time periods")
            elif pattern_name == QueryPattern.CATEGORICAL_COMPARISON.value:
                suggestions.append("Compare performance across different categories")
        
        # Field-based suggestions
        if profile.common_fields:
            field = profile.common_fields[-1]  # Most recent field
            suggestions.append(f"Explore {field} data with different visualizations")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _get_default_suggestions(self) -> List[str]:
        """Get default suggestions for new users."""
        return [
            "Start with a simple data overview",
            "Try creating a chart to visualize your data",
            "Explore trends over time",
            "Compare different categories",
            "Look for patterns in your data"
        ]
    
    async def get_intelligence_metrics(self) -> Dict[str, Any]:
        """Get intelligence service metrics."""
        
        total_profiles = len(self.user_profiles)
        
        # Behavior distribution
        behavior_counts = Counter(
            profile.behavior_type.value for profile in self.user_profiles.values()
        )
        
        # Pattern distribution
        pattern_counts = defaultdict(int)
        for profile in self.user_profiles.values():
            for pattern, count in profile.interaction_patterns.items():
                pattern_counts[pattern] += count
        
        # Average complexity
        avg_complexity = np.mean([
            profile.query_complexity for profile in self.user_profiles.values()
        ]) if self.user_profiles else 0.0
        
        return {
            "total_user_profiles": total_profiles,
            "behavior_distribution": dict(behavior_counts),
            "pattern_distribution": dict(pattern_counts),
            "average_query_complexity": avg_complexity,
            "active_sessions": len([
                p for p in self.user_profiles.values()
                if (datetime.now() - p.last_updated).seconds < 3600  # Active in last hour
            ])
        }


# Global service instance
query_intelligence_service = QueryIntelligenceService()