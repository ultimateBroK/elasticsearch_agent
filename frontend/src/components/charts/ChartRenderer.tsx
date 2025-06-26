'use client'

import React, { useState, useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useChart } from '@/hooks/useChart'
import { ChartType } from '@/types/api'

interface ChartData {
  [key: string]: any
}

interface ChartConfig {
  chart_type: string
  title: string
  has_data: boolean
  data_count?: number
  use_aggregations?: boolean
  aggregation_data?: any
  suggested_fields?: {
    numeric: string[]
    text: string[]
    date: string[]
  }
  x_axis_suggestion?: string
  y_axis_suggestion?: string
  label_field?: string
  value_field?: string
}

interface ChartRendererProps {
  chartConfig: ChartConfig
  data: ChartData[]
}

export function ChartRenderer({ chartConfig, data }: ChartRendererProps) {
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const {
    config: enhancedConfig,
    chartType,
    setChartType,
    getRecommendedChartTypes,
    validateConfig,
    errors
  } = useChart(chartConfig)

  // Get recommended chart types for this data
  const recommendedTypes = useMemo(() => {
    if (!data || data.length === 0) return []
    return getRecommendedChartTypes(data)
  }, [data, getRecommendedChartTypes])

  if (!chartConfig.has_data || !data || data.length === 0) {
    return (
      <Card className="mt-3">
        <CardHeader>
          <CardTitle className="text-sm">📊 {chartConfig.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            No data available for visualization
          </div>
        </CardContent>
      </Card>
    )
  }

  if (errors.length > 0) {
    return (
      <Card className="mt-3 border-yellow-200 bg-yellow-50">
        <CardHeader>
          <CardTitle className="text-sm text-yellow-800">⚠️ Chart Configuration Issues</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {errors.map((error, index) => (
              <div key={index} className="text-sm text-yellow-700">
                • {error}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const generateChartOption = () => {
    const { chart_type, suggested_fields, x_axis_suggestion, y_axis_suggestion, label_field, value_field } = chartConfig

    // Use aggregation data if available, otherwise use raw data
    const chartData = chartConfig.use_aggregations && chartConfig.aggregation_data 
      ? processAggregationData(chartConfig.aggregation_data)
      : data.slice(0, 50) // Limit to 50 items for performance

    switch (chart_type?.toLowerCase()) {
      case 'bar':
        return generateBarChart(chartData, x_axis_suggestion, y_axis_suggestion, suggested_fields)
      case 'line':
        return generateLineChart(chartData, x_axis_suggestion, y_axis_suggestion, suggested_fields)
      case 'pie':
        return generatePieChart(chartData, label_field, value_field, suggested_fields)
      case 'scatter':
        return generateScatterChart(chartData, x_axis_suggestion, y_axis_suggestion, suggested_fields)
      case 'area':
        return generateAreaChart(chartData, x_axis_suggestion, y_axis_suggestion, suggested_fields)
      default:
        return generateBarChart(chartData, x_axis_suggestion, y_axis_suggestion, suggested_fields)
    }
  }

  const processAggregationData = (aggregationData: any) => {
    // Process Elasticsearch aggregation results
    // This is a simplified version - can be enhanced based on actual aggregation structure
    if (aggregationData.buckets) {
      return aggregationData.buckets.map((bucket: any) => ({
        name: bucket.key,
        value: bucket.doc_count,
        ...bucket
      }))
    }
    return []
  }

  const generateBarChart = (chartData: any[], xField?: string, yField?: string, suggestedFields?: any) => {
    const firstItem = chartData && chartData.length > 0 ? chartData[0] : {}
    const xAxis = xField || suggestedFields?.text?.[0] || Object.keys(firstItem)[0] || 'category'
    const yAxis = yField || suggestedFields?.numeric?.[0] || 'value'

    return {
      title: {
        text: chartConfig.title,
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.map(item => item[xAxis] || item.name || 'Unknown'),
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: yAxis,
        type: 'bar',
        data: chartData.map(item => item[yAxis] || item.value || 0),
        itemStyle: {
          color: '#3b82f6'
        }
      }]
    }
  }

  const generateLineChart = (chartData: any[], xField?: string, yField?: string, suggestedFields?: any) => {
    const firstItem = chartData && chartData.length > 0 ? chartData[0] : {}
    const xAxis = xField || suggestedFields?.date?.[0] || suggestedFields?.text?.[0] || Object.keys(firstItem)[0] || 'category'
    const yAxis = yField || suggestedFields?.numeric?.[0] || 'value'

    return {
      title: {
        text: chartConfig.title,
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.map(item => item[xAxis] || item.name || 'Unknown'),
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: yAxis,
        type: 'line',
        data: chartData.map(item => item[yAxis] || item.value || 0),
        smooth: true,
        lineStyle: {
          color: '#10b981'
        },
        itemStyle: {
          color: '#10b981'
        }
      }]
    }
  }

  const generatePieChart = (chartData: any[], labelField?: string, valueField?: string, suggestedFields?: any) => {
    const label = labelField || suggestedFields?.text?.[0] || 'name'
    const value = valueField || suggestedFields?.numeric?.[0] || 'value'

    return {
      title: {
        text: chartConfig.title,
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: chartConfig.title,
        type: 'pie',
        radius: '50%',
        data: chartData.map(item => ({
          name: item[label] || item.name || 'Unknown',
          value: item[value] || item.value || 0
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
  }

  const generateScatterChart = (chartData: any[], xField?: string, yField?: string, suggestedFields?: any) => {
    const firstItem = chartData && chartData.length > 0 ? chartData[0] : {}
    const xAxis = xField || suggestedFields?.numeric?.[0] || Object.keys(firstItem)[0] || 'x'
    const yAxis = yField || suggestedFields?.numeric?.[1] || suggestedFields?.numeric?.[0] || 'value'

    return {
      title: {
        text: chartConfig.title,
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'item'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: xAxis
      },
      yAxis: {
        type: 'value',
        name: yAxis
      },
      series: [{
        name: 'Data Points',
        type: 'scatter',
        data: chartData.map(item => [
          item[xAxis] || 0,
          item[yAxis] || item.value || 0
        ]),
        itemStyle: {
          color: '#8b5cf6'
        }
      }]
    }
  }

  const generateAreaChart = (chartData: any[], xField?: string, yField?: string, suggestedFields?: any) => {
    const firstItem = chartData && chartData.length > 0 ? chartData[0] : {}
    const xAxis = xField || suggestedFields?.date?.[0] || suggestedFields?.text?.[0] || Object.keys(firstItem)[0] || 'category'
    const yAxis = yField || suggestedFields?.numeric?.[0] || 'value'

    return {
      title: {
        text: chartConfig.title,
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.map(item => item[xAxis] || item.name || 'Unknown'),
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: yAxis,
        type: 'line',
        data: chartData.map(item => item[yAxis] || item.value || 0),
        areaStyle: {
          color: 'rgba(59, 130, 246, 0.3)'
        },
        lineStyle: {
          color: '#3b82f6'
        },
        itemStyle: {
          color: '#3b82f6'
        }
      }]
    }
  }

  const option = useMemo(() => {
    try {
      setError(null)
      return generateChartOption()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate chart'
      setError(errorMessage)
      return null
    }
  }, [chartType, data, chartConfig])

  if (error) {
    return (
      <Card className="mt-3 border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="text-sm text-red-800">❌ Chart Error</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-red-700 mb-3">{error}</div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setError(null)}
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!option) {
    return (
      <Card className="mt-3">
        <CardHeader>
          <CardTitle className="text-sm">📊 {chartConfig.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            Unable to generate chart configuration
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="mt-3">
      <CardHeader>
        <CardTitle className="text-sm">📊 {chartConfig.title}</CardTitle>
        
        {/* Enhanced recommendation info */}
        {chartConfig.confidence && (
          <div className="text-xs text-muted-foreground mb-2">
            <Badge variant="secondary" className="mr-2">
              {(chartConfig.confidence * 100).toFixed(0)}% confidence
            </Badge>
            {chartConfig.reasoning && (
              <span className="italic">{chartConfig.reasoning}</span>
            )}
          </div>
        )}
        
        {/* AI explanation */}
        {chartConfig.ai_explanation && (
          <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded mb-2">
            💡 {chartConfig.ai_explanation}
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            {chartConfig.data_count} records
            {chartConfig.data_profile && (
              <span className="ml-2">
                • {chartConfig.data_profile.numeric_fields.length} numeric
                • {chartConfig.data_profile.categorical_fields.length} categorical
                {chartConfig.data_profile.temporal_fields.length > 0 && (
                  <span> • {chartConfig.data_profile.temporal_fields.length} temporal</span>
                )}
              </span>
            )}
          </div>
          
          {/* Chart type selector with alternatives */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-muted-foreground">Type:</span>
            {/* Primary recommendation */}
            <Button
              size="sm"
              variant={chartType === chartConfig.chart_type ? "default" : "outline"}
              onClick={() => setChartType(chartConfig.chart_type)}
              className="text-xs h-6 px-2"
              title={chartConfig.reasoning || "Primary recommendation"}
            >
              {chartConfig.chart_type}
              {chartConfig.confidence && (
                <span className="ml-1 text-xs opacity-70">
                  {(chartConfig.confidence * 100).toFixed(0)}%
                </span>
              )}
            </Button>
            
            {/* Alternative recommendations */}
            {chartConfig.alternative_charts?.map((alt, index) => (
              <Button
                key={`alt-${index}`}
                size="sm"
                variant={chartType === alt.type ? "default" : "outline"}
                onClick={() => setChartType(alt.type as ChartType)}
                className="text-xs h-6 px-2 opacity-75"
                title={alt.reasoning}
              >
                {alt.type}
                <span className="ml-1 text-xs opacity-70">
                  {(alt.confidence * 100).toFixed(0)}%
                </span>
              </Button>
            ))}
            
            {/* Fallback to basic recommendations */}
            {recommendedTypes.filter(type => 
              type !== chartConfig.chart_type && 
              !chartConfig.alternative_charts?.some(alt => alt.type === type)
            ).map((type) => (
              <Button
                key={type}
                size="sm"
                variant={chartType === type ? "default" : "outline"}
                onClick={() => setChartType(type)}
                className="text-xs h-6 px-2 opacity-50"
              >
                {type}
              </Button>
            ))}
          </div>
        </div>
        
        {/* Data characteristics */}
        {chartConfig.data_profile?.data_characteristics && (
          <div className="flex flex-wrap gap-1 mt-2">
            {chartConfig.data_profile.data_characteristics.map((characteristic, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {characteristic.replace('_', ' ')}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <ReactECharts
          option={option}
          style={{ height: '400px', width: '100%' }}
          opts={{ renderer: 'canvas' }}
          onError={(error) => {
            console.error('ECharts error:', error)
            setError('Chart rendering failed')
          }}
          showLoading={isLoading}
          loadingOption={{
            text: 'Loading chart...',
            color: '#3b82f6',
            textColor: '#374151',
            maskColor: 'rgba(255, 255, 255, 0.8)'
          }}
        />
      </CardContent>
    </Card>
  )
}