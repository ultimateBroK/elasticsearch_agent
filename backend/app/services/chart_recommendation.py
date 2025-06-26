"""Advanced chart recommendation service using ML-based analysis."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from collections import Counter

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX = "box"


class DataCharacteristic(Enum):
    """Data characteristics for recommendation."""
    TEMPORAL = "temporal"
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    HIERARCHICAL = "hierarchical"


@dataclass
class ChartRecommendation:
    """Chart recommendation with confidence score."""
    chart_type: ChartType
    confidence: float
    reasoning: str
    suggested_fields: Dict[str, str]
    configuration: Dict[str, Any]


@dataclass
class DataProfile:
    """Profile of the dataset for recommendation."""
    total_records: int
    field_types: Dict[str, str]
    numeric_fields: List[str]
    categorical_fields: List[str]
    temporal_fields: List[str]
    unique_values: Dict[str, int]
    null_percentages: Dict[str, float]
    data_characteristics: List[DataCharacteristic]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]]


class ChartRecommendationService:
    """Advanced chart recommendation service."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.recommendation_rules = self._build_recommendation_rules()
        
    def _build_recommendation_rules(self) -> Dict[str, Any]:
        """Build recommendation rules based on data characteristics."""
        return {
            # Time series patterns
            "temporal_numeric": {
                "primary": [ChartType.LINE, ChartType.AREA],
                "secondary": [ChartType.BAR],
                "confidence_boost": 0.3
            },
            
            # Categorical analysis
            "categorical_numeric": {
                "primary": [ChartType.BAR, ChartType.PIE],
                "secondary": [ChartType.HISTOGRAM],
                "confidence_boost": 0.2
            },
            
            # Correlation analysis
            "numeric_correlation": {
                "primary": [ChartType.SCATTER, ChartType.HEATMAP],
                "secondary": [ChartType.LINE],
                "confidence_boost": 0.4
            },
            
            # Distribution analysis
            "distribution": {
                "primary": [ChartType.HISTOGRAM, ChartType.BOX],
                "secondary": [ChartType.BAR],
                "confidence_boost": 0.25
            },
            
            # Small categorical datasets
            "small_categorical": {
                "primary": [ChartType.PIE, ChartType.BAR],
                "secondary": [ChartType.AREA],
                "confidence_boost": 0.3
            }
        }
    
    def analyze_data(self, data: List[Dict[str, Any]]) -> DataProfile:
        """Analyze dataset to create a data profile."""
        if not data:
            return DataProfile(
                total_records=0,
                field_types={},
                numeric_fields=[],
                categorical_fields=[],
                temporal_fields=[],
                unique_values={},
                null_percentages={},
                data_characteristics=[],
                correlation_matrix=None
            )
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(data)
            
            # Basic statistics
            total_records = len(df)
            field_types = {}
            numeric_fields = []
            categorical_fields = []
            temporal_fields = []
            unique_values = {}
            null_percentages = {}
            
            for column in df.columns:
                # Determine field type
                if df[column].dtype in ['int64', 'float64']:
                    field_types[column] = 'numeric'
                    numeric_fields.append(column)
                elif df[column].dtype == 'object':
                    # Check if it's temporal
                    if any(keyword in column.lower() for keyword in ['date', 'time', 'timestamp']):
                        field_types[column] = 'temporal'
                        temporal_fields.append(column)
                    else:
                        field_types[column] = 'categorical'
                        categorical_fields.append(column)
                else:
                    field_types[column] = 'other'
                
                # Count unique values
                unique_values[column] = df[column].nunique()
                
                # Calculate null percentage
                null_percentages[column] = (df[column].isnull().sum() / len(df)) * 100
            
            # Determine data characteristics
            characteristics = self._identify_characteristics(
                df, numeric_fields, categorical_fields, temporal_fields, unique_values
            )
            
            # Calculate correlation matrix for numeric fields
            correlation_matrix = None
            if len(numeric_fields) >= 2:
                try:
                    corr_df = df[numeric_fields].corr()
                    correlation_matrix = corr_df.to_dict()
                except Exception as e:
                    logger.warning(f"Failed to calculate correlation matrix: {e}")
            
            return DataProfile(
                total_records=total_records,
                field_types=field_types,
                numeric_fields=numeric_fields,
                categorical_fields=categorical_fields,
                temporal_fields=temporal_fields,
                unique_values=unique_values,
                null_percentages=null_percentages,
                data_characteristics=characteristics,
                correlation_matrix=correlation_matrix
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze data: {e}")
            return DataProfile(
                total_records=len(data),
                field_types={},
                numeric_fields=[],
                categorical_fields=[],
                temporal_fields=[],
                unique_values={},
                null_percentages={},
                data_characteristics=[],
                correlation_matrix=None
            )
    
    def _identify_characteristics(
        self,
        df: pd.DataFrame,
        numeric_fields: List[str],
        categorical_fields: List[str],
        temporal_fields: List[str],
        unique_values: Dict[str, int]
    ) -> List[DataCharacteristic]:
        """Identify data characteristics for recommendation."""
        characteristics = []
        
        # Temporal data
        if temporal_fields and numeric_fields:
            characteristics.append(DataCharacteristic.TEMPORAL)
        
        # Categorical data
        if categorical_fields and numeric_fields:
            characteristics.append(DataCharacteristic.CATEGORICAL)
        
        # Numerical data
        if len(numeric_fields) >= 2:
            characteristics.append(DataCharacteristic.NUMERICAL)
            
            # Check for correlation
            try:
                corr_matrix = df[numeric_fields].corr()
                max_correlation = corr_matrix.abs().max().max()
                if max_correlation > 0.7:  # Strong correlation threshold
                    characteristics.append(DataCharacteristic.CORRELATION)
            except Exception:
                pass
        
        # Distribution analysis
        if len(numeric_fields) >= 1:
            characteristics.append(DataCharacteristic.DISTRIBUTION)
        
        # Hierarchical data (based on field names and structure)
        hierarchical_keywords = ['parent', 'child', 'level', 'category', 'subcategory']
        if any(keyword in ' '.join(df.columns).lower() for keyword in hierarchical_keywords):
            characteristics.append(DataCharacteristic.HIERARCHICAL)
        
        return characteristics
    
    def recommend_charts(
        self,
        data: List[Dict[str, Any]],
        intent: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[ChartRecommendation]:
        """Generate chart recommendations based on data analysis."""
        
        # Analyze the data
        profile = self.analyze_data(data)
        
        if profile.total_records == 0:
            return []
        
        recommendations = []
        
        # Apply recommendation rules based on characteristics
        for characteristic in profile.data_characteristics:
            chart_recs = self._apply_characteristic_rules(characteristic, profile, intent)
            recommendations.extend(chart_recs)
        
        # Apply intent-based recommendations
        if intent:
            intent_recs = self._apply_intent_rules(intent, profile)
            recommendations.extend(intent_recs)
        
        # Apply user preference adjustments
        if user_preferences:
            recommendations = self._apply_user_preferences(recommendations, user_preferences)
        
        # Sort by confidence and remove duplicates
        unique_recommendations = {}
        for rec in recommendations:
            key = rec.chart_type.value
            if key not in unique_recommendations or rec.confidence > unique_recommendations[key].confidence:
                unique_recommendations[key] = rec
        
        # Sort by confidence score
        final_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda x: x.confidence,
            reverse=True
        )
        
        return final_recommendations[:5]  # Return top 5 recommendations
    
    def _apply_characteristic_rules(
        self,
        characteristic: DataCharacteristic,
        profile: DataProfile,
        intent: Optional[str]
    ) -> List[ChartRecommendation]:
        """Apply rules based on data characteristics."""
        recommendations = []
        
        if characteristic == DataCharacteristic.TEMPORAL:
            # Time series recommendations
            if profile.temporal_fields and profile.numeric_fields:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.LINE,
                    confidence=0.9,
                    reasoning="Time series data is best visualized with line charts",
                    suggested_fields={
                        "x_axis": profile.temporal_fields[0],
                        "y_axis": profile.numeric_fields[0]
                    },
                    configuration={
                        "smooth_line": True,
                        "show_points": len(profile.temporal_fields) < 50
                    }
                ))
                
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.AREA,
                    confidence=0.8,
                    reasoning="Area charts show cumulative trends over time",
                    suggested_fields={
                        "x_axis": profile.temporal_fields[0],
                        "y_axis": profile.numeric_fields[0]
                    },
                    configuration={"fill_opacity": 0.3}
                ))
        
        elif characteristic == DataCharacteristic.CATEGORICAL:
            # Categorical recommendations
            if profile.categorical_fields and profile.numeric_fields:
                cat_field = profile.categorical_fields[0]
                unique_count = profile.unique_values.get(cat_field, 0)
                
                if unique_count <= 8:
                    recommendations.append(ChartRecommendation(
                        chart_type=ChartType.PIE,
                        confidence=0.85,
                        reasoning=f"Pie chart works well for {unique_count} categories",
                        suggested_fields={
                            "label": cat_field,
                            "value": profile.numeric_fields[0]
                        },
                        configuration={"show_percentages": True}
                    ))
                
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.BAR,
                    confidence=0.8,
                    reasoning="Bar charts effectively compare categorical data",
                    suggested_fields={
                        "x_axis": cat_field,
                        "y_axis": profile.numeric_fields[0]
                    },
                    configuration={
                        "sort_by_value": unique_count > 5,
                        "rotate_labels": unique_count > 10
                    }
                ))
        
        elif characteristic == DataCharacteristic.CORRELATION:
            # Correlation recommendations
            if len(profile.numeric_fields) >= 2:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.SCATTER,
                    confidence=0.9,
                    reasoning="Scatter plots reveal correlations between variables",
                    suggested_fields={
                        "x_axis": profile.numeric_fields[0],
                        "y_axis": profile.numeric_fields[1]
                    },
                    configuration={
                        "show_trend_line": True,
                        "point_size": "auto"
                    }
                ))
        
        elif characteristic == DataCharacteristic.DISTRIBUTION:
            # Distribution recommendations
            if profile.numeric_fields:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.HISTOGRAM,
                    confidence=0.75,
                    reasoning="Histograms show data distribution patterns",
                    suggested_fields={
                        "value": profile.numeric_fields[0]
                    },
                    configuration={
                        "bins": "auto",
                        "show_density": True
                    }
                ))
        
        return recommendations
    
    def _apply_intent_rules(
        self,
        intent: str,
        profile: DataProfile
    ) -> List[ChartRecommendation]:
        """Apply recommendations based on user intent."""
        recommendations = []
        intent_lower = intent.lower()
        
        # Trend analysis intent
        if any(keyword in intent_lower for keyword in ['trend', 'over time', 'timeline', 'progression']):
            if profile.temporal_fields and profile.numeric_fields:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.LINE,
                    confidence=0.95,
                    reasoning="Line charts are ideal for trend analysis",
                    suggested_fields={
                        "x_axis": profile.temporal_fields[0],
                        "y_axis": profile.numeric_fields[0]
                    },
                    configuration={"show_trend_line": True}
                ))
        
        # Comparison intent
        elif any(keyword in intent_lower for keyword in ['compare', 'comparison', 'versus', 'vs']):
            if profile.categorical_fields and profile.numeric_fields:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.BAR,
                    confidence=0.9,
                    reasoning="Bar charts excel at comparing categories",
                    suggested_fields={
                        "x_axis": profile.categorical_fields[0],
                        "y_axis": profile.numeric_fields[0]
                    },
                    configuration={"sort_by_value": True}
                ))
        
        # Distribution intent
        elif any(keyword in intent_lower for keyword in ['distribution', 'spread', 'range']):
            if profile.numeric_fields:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.HISTOGRAM,
                    confidence=0.9,
                    reasoning="Histograms show data distribution",
                    suggested_fields={
                        "value": profile.numeric_fields[0]
                    },
                    configuration={"bins": 20}
                ))
        
        # Relationship intent
        elif any(keyword in intent_lower for keyword in ['relationship', 'correlation', 'association']):
            if len(profile.numeric_fields) >= 2:
                recommendations.append(ChartRecommendation(
                    chart_type=ChartType.SCATTER,
                    confidence=0.95,
                    reasoning="Scatter plots reveal relationships between variables",
                    suggested_fields={
                        "x_axis": profile.numeric_fields[0],
                        "y_axis": profile.numeric_fields[1]
                    },
                    configuration={"show_correlation": True}
                ))
        
        return recommendations
    
    def _apply_user_preferences(
        self,
        recommendations: List[ChartRecommendation],
        preferences: Dict[str, Any]
    ) -> List[ChartRecommendation]:
        """Adjust recommendations based on user preferences."""
        
        # Preferred chart types
        preferred_types = preferences.get('preferred_chart_types', [])
        if preferred_types:
            for rec in recommendations:
                if rec.chart_type.value in preferred_types:
                    rec.confidence = min(1.0, rec.confidence + 0.1)
        
        # Complexity preference
        complexity = preferences.get('complexity', 'medium')
        if complexity == 'simple':
            # Boost simple chart types
            simple_types = [ChartType.BAR, ChartType.PIE, ChartType.LINE]
            for rec in recommendations:
                if rec.chart_type in simple_types:
                    rec.confidence = min(1.0, rec.confidence + 0.05)
        elif complexity == 'advanced':
            # Boost complex chart types
            complex_types = [ChartType.SCATTER, ChartType.HEATMAP, ChartType.BOX]
            for rec in recommendations:
                if rec.chart_type in complex_types:
                    rec.confidence = min(1.0, rec.confidence + 0.05)
        
        return recommendations
    
    def explain_recommendation(
        self,
        recommendation: ChartRecommendation,
        profile: DataProfile
    ) -> str:
        """Generate detailed explanation for a recommendation."""
        
        explanation_parts = [
            f"**{recommendation.chart_type.value.title()} Chart** (Confidence: {recommendation.confidence:.1%})",
            "",
            f"**Reasoning:** {recommendation.reasoning}",
            "",
            "**Data Analysis:**"
        ]
        
        if profile.total_records:
            explanation_parts.append(f"- Dataset contains {profile.total_records:,} records")
        
        if profile.numeric_fields:
            explanation_parts.append(f"- {len(profile.numeric_fields)} numeric fields: {', '.join(profile.numeric_fields[:3])}")
        
        if profile.categorical_fields:
            explanation_parts.append(f"- {len(profile.categorical_fields)} categorical fields: {', '.join(profile.categorical_fields[:3])}")
        
        if profile.temporal_fields:
            explanation_parts.append(f"- {len(profile.temporal_fields)} temporal fields: {', '.join(profile.temporal_fields)}")
        
        explanation_parts.extend([
            "",
            "**Suggested Configuration:**"
        ])
        
        for field_type, field_name in recommendation.suggested_fields.items():
            explanation_parts.append(f"- {field_type.replace('_', ' ').title()}: {field_name}")
        
        if recommendation.configuration:
            explanation_parts.append("")
            explanation_parts.append("**Additional Settings:**")
            for setting, value in recommendation.configuration.items():
                explanation_parts.append(f"- {setting.replace('_', ' ').title()}: {value}")
        
        return "\n".join(explanation_parts)


# Global service instance
chart_recommendation_service = ChartRecommendationService()