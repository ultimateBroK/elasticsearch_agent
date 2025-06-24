"use client"

import { useState, useCallback, useMemo } from 'react'
import { ChartConfig, ChartType } from '@/types/api'

interface UseChartOptions {
  onChartTypeChange?: (chartType: ChartType) => void
  onConfigChange?: (config: ChartConfig) => void
}

interface ChartState {
  selectedType: ChartType
  customConfig: Partial<ChartConfig>
  isCustomizing: boolean
}

export function useChart(
  initialConfig?: ChartConfig,
  options: UseChartOptions = {}
) {
  const [state, setState] = useState<ChartState>({
    selectedType: initialConfig?.chart_type || ChartType.BAR,
    customConfig: {},
    isCustomizing: false
  })

  // Merge initial config with custom overrides
  const finalConfig = useMemo((): ChartConfig | null => {
    if (!initialConfig) return null

    return {
      ...initialConfig,
      chart_type: state.selectedType,
      ...state.customConfig
    }
  }, [initialConfig, state.selectedType, state.customConfig])

  const setChartType = useCallback((chartType: ChartType) => {
    setState(prev => ({ ...prev, selectedType: chartType }))
    options.onChartTypeChange?.(chartType)
  }, [options])

  const updateConfig = useCallback((updates: Partial<ChartConfig>) => {
    setState(prev => ({
      ...prev,
      customConfig: { ...prev.customConfig, ...updates }
    }))
    
    if (finalConfig) {
      options.onConfigChange?.({ ...finalConfig, ...updates })
    }
  }, [finalConfig, options])

  const resetCustomization = useCallback(() => {
    setState(prev => ({
      ...prev,
      customConfig: {},
      isCustomizing: false
    }))
  }, [])

  const toggleCustomization = useCallback(() => {
    setState(prev => ({ ...prev, isCustomizing: !prev.isCustomizing }))
  }, [])

  // Chart type recommendations based on data characteristics
  const getRecommendedChartTypes = useCallback((data: any[]): ChartType[] => {
    if (!data || data.length === 0) return [ChartType.BAR]

    const recommendations: ChartType[] = []
    const sample = data[0]
    const fields = Object.keys(sample)
    
    const numericFields = fields.filter(field => 
      typeof sample[field] === 'number'
    )
    
    const textFields = fields.filter(field => 
      typeof sample[field] === 'string'
    )
    
    const dateFields = fields.filter(field => 
      field.toLowerCase().includes('date') || 
      field.toLowerCase().includes('time') ||
      field.toLowerCase().includes('timestamp')
    )

    // Time series data
    if (dateFields.length > 0 && numericFields.length > 0) {
      recommendations.push(ChartType.LINE, ChartType.AREA)
    }

    // Categorical data
    if (textFields.length > 0 && numericFields.length > 0) {
      recommendations.push(ChartType.BAR)
      
      // If few categories, pie chart is good
      const uniqueValues = new Set(data.map(item => item[textFields[0]]))
      if (uniqueValues.size <= 8) {
        recommendations.push(ChartType.PIE)
      }
    }

    // Correlation analysis
    if (numericFields.length >= 2) {
      recommendations.push(ChartType.SCATTER)
    }

    // Default fallback
    if (recommendations.length === 0) {
      recommendations.push(ChartType.BAR)
    }

    return recommendations
  }, [])

  // Validate chart configuration
  const validateConfig = useCallback((config: ChartConfig): string[] => {
    const errors: string[] = []

    if (!config.title || config.title.trim() === '') {
      errors.push('Chart title is required')
    }

    if (!config.has_data) {
      errors.push('No data available for visualization')
    }

    if (config.chart_type === ChartType.PIE) {
      if (!config.label_field) {
        errors.push('Pie charts require a label field')
      }
      if (!config.value_field) {
        errors.push('Pie charts require a value field')
      }
    }

    if ([ChartType.LINE, ChartType.AREA, ChartType.BAR].includes(config.chart_type)) {
      if (!config.x_axis_suggestion && !config.suggested_fields?.text?.length) {
        errors.push('Chart requires an X-axis field')
      }
      if (!config.y_axis_suggestion && !config.suggested_fields?.numeric?.length) {
        errors.push('Chart requires a Y-axis field')
      }
    }

    if (config.chart_type === ChartType.SCATTER) {
      if (!config.suggested_fields?.numeric || config.suggested_fields.numeric.length < 2) {
        errors.push('Scatter plots require at least 2 numeric fields')
      }
    }

    return errors
  }, [])

  return {
    config: finalConfig,
    chartType: state.selectedType,
    isCustomizing: state.isCustomizing,
    setChartType,
    updateConfig,
    resetCustomization,
    toggleCustomization,
    getRecommendedChartTypes,
    validateConfig,
    errors: finalConfig ? validateConfig(finalConfig) : []
  }
}