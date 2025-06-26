"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chatStore'

interface QueryInsight {
  pattern: string
  confidence: number
  reasoning: string
  suggested_improvements: string[]
  related_patterns: string[]
  user_behavior_hint?: string
}

interface IntelligenceMetrics {
  pattern?: string
  confidence?: number
  user_behavior?: string
}

interface IntelligenceInsightsProps {
  queryInsight?: QueryInsight
  personalizedSuggestions?: string[]
  intelligenceMetrics?: IntelligenceMetrics
  onSuggestionClick?: (suggestion: string) => void
  onFeedback?: (feedback: { satisfaction: number; chart_rating: number }) => void
}

export function IntelligenceInsights({
  queryInsight,
  personalizedSuggestions = [],
  intelligenceMetrics,
  onSuggestionClick,
  onFeedback
}: IntelligenceInsightsProps) {
  const [showDetails, setShowDetails] = useState(false)
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const { sessionId } = useChatStore()

  // Don't render if no intelligence data
  if (!queryInsight && !personalizedSuggestions.length && !intelligenceMetrics) {
    return null
  }

  const handleSuggestionClick = (suggestion: string) => {
    if (onSuggestionClick) {
      onSuggestionClick(suggestion)
    }
  }

  const handleFeedback = (satisfaction: number, chartRating: number = 0.5) => {
    if (onFeedback && !feedbackGiven) {
      onFeedback({ satisfaction, chart_rating: chartRating })
      setFeedbackGiven(true)
    }
  }

  const getPatternIcon = (pattern: string) => {
    const patternIcons: Record<string, string> = {
      'time_series_analysis': '📈',
      'categorical_comparison': '📊',
      'aggregation_summary': '🔢',
      'correlation_analysis': '🔗',
      'distribution_analysis': '📉',
      'trend_analysis': '📈',
      'anomaly_detection': '🚨',
      'drill_down': '🔍',
      'roll_up': '📋',
      'filter_refinement': '🔧'
    }
    return patternIcons[pattern] || '🧠'
  }

  const getBehaviorIcon = (behavior: string) => {
    const behaviorIcons: Record<string, string> = {
      'explorer': '🧭',
      'analyst': '🔬', 
      'reporter': '📝',
      'casual': '👤'
    }
    return behaviorIcons[behavior] || '👤'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <Card className="mt-3 border-blue-200 bg-blue-50/50">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            🧠 Intelligence Insights
            {intelligenceMetrics?.confidence && (
              <Badge className={getConfidenceColor(intelligenceMetrics.confidence)}>
                {(intelligenceMetrics.confidence * 100).toFixed(0)}% confidence
              </Badge>
            )}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs"
          >
            {showDetails ? 'Hide' : 'Show'} Details
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-3">
        {/* Query Pattern Analysis */}
        {queryInsight && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">{getPatternIcon(queryInsight.pattern)}</span>
              <div>
                <div className="text-sm font-medium">
                  {queryInsight.pattern.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Pattern
                </div>
                <div className="text-xs text-muted-foreground">
                  {queryInsight.reasoning}
                </div>
              </div>
            </div>

            {showDetails && (
              <div className="space-y-2 pl-6 border-l-2 border-blue-200">
                {/* User Behavior */}
                {queryInsight.user_behavior_hint && (
                  <div className="flex items-center gap-2 text-xs">
                    <span>{getBehaviorIcon(queryInsight.user_behavior_hint)}</span>
                    <span className="font-medium">User Type:</span>
                    <Badge variant="outline" className="text-xs">
                      {queryInsight.user_behavior_hint.replace(/\b\w/g, l => l.toUpperCase())}
                    </Badge>
                  </div>
                )}

                {/* Improvements */}
                {queryInsight.suggested_improvements.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-xs font-medium text-blue-700">💡 Suggestions:</div>
                    {queryInsight.suggested_improvements.slice(0, 3).map((improvement, index) => (
                      <div key={index} className="text-xs text-muted-foreground pl-4">
                        • {improvement}
                      </div>
                    ))}
                  </div>
                )}

                {/* Related Patterns */}
                {queryInsight.related_patterns.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-xs font-medium text-blue-700">🔗 Related Patterns:</div>
                    <div className="flex flex-wrap gap-1">
                      {queryInsight.related_patterns.map((pattern, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {pattern.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Personalized Suggestions */}
        {personalizedSuggestions.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium text-blue-700 flex items-center gap-1">
              🎯 Personalized Suggestions
            </div>
            <div className="space-y-1">
              {personalizedSuggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left text-xs p-2 rounded bg-white hover:bg-blue-50 border border-blue-200 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Intelligence Metrics */}
        {intelligenceMetrics && showDetails && (
          <div className="space-y-2 pt-2 border-t border-blue-200">
            <div className="text-xs font-medium text-blue-700">📊 Session Analytics</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {intelligenceMetrics.pattern && (
                <div>
                  <span className="text-muted-foreground">Pattern:</span>
                  <div className="font-medium">{intelligenceMetrics.pattern.replace(/_/g, ' ')}</div>
                </div>
              )}
              {intelligenceMetrics.user_behavior && (
                <div>
                  <span className="text-muted-foreground">Behavior:</span>
                  <div className="font-medium">{intelligenceMetrics.user_behavior}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Feedback Section */}
        {!feedbackGiven && queryInsight && (
          <div className="pt-2 border-t border-blue-200">
            <div className="text-xs font-medium text-blue-700 mb-2">📝 How helpful was this analysis?</div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleFeedback(0.9, 0.8)}
                className="text-xs h-7"
              >
                👍 Very helpful
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleFeedback(0.6, 0.6)}
                className="text-xs h-7"
              >
                👌 Somewhat helpful
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleFeedback(0.3, 0.3)}
                className="text-xs h-7"
              >
                👎 Not helpful
              </Button>
            </div>
          </div>
        )}

        {feedbackGiven && (
          <div className="pt-2 border-t border-blue-200">
            <div className="text-xs text-green-600 flex items-center gap-1">
              ✅ Thank you for your feedback! This helps improve our recommendations.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}