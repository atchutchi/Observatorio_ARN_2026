'use client'

import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

type BarSeriesItem = {
  name: string
  data: number[]
  color: string
  stack?: string
}

type LineSeriesItem = {
  name: string
  data: number[]
  color: string
  yAxisIndex?: number
}

type ComboChartProps = {
  categories: string[]
  barSeries: BarSeriesItem[]
  lineSeries: LineSeriesItem[]
  height?: number
  showLegend?: boolean
  yAxisLabel?: string
  yAxisRightLabel?: string
  stacked?: boolean
  formatValue?: (val: number) => string
}

const defaultFormat = (val: number) => {
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`
  return String(val)
}

const ComboChart = ({
  categories,
  barSeries,
  lineSeries,
  height = 350,
  showLegend = true,
  yAxisLabel,
  yAxisRightLabel,
  stacked = false,
  formatValue = defaultFormat,
}: ComboChartProps) => {
  const hasRightAxis = lineSeries.some((s) => s.yAxisIndex === 1) || !!yAxisRightLabel
  const allNames = [...barSeries.map((s) => s.name), ...lineSeries.map((s) => s.name)]

  const yAxis: object[] = [
    {
      type: 'value',
      name: yAxisLabel,
      axisLabel: { formatter: formatValue },
    },
  ]

  if (hasRightAxis) {
    yAxis.push({
      type: 'value',
      name: yAxisRightLabel || '%',
      axisLabel: { formatter: (v: number) => `${v}%` },
      splitLine: { show: false },
    })
  }

  const option = {
    tooltip: { trigger: 'axis' as const },
    legend: showLegend ? { data: allNames, bottom: 0 } : undefined,
    grid: {
      left: '3%',
      right: hasRightAxis ? '8%' : '4%',
      bottom: showLegend ? '15%' : '5%',
      top: '12%',
      containLabel: true,
    },
    xAxis: {
      type: 'category' as const,
      data: categories,
    },
    yAxis,
    series: [
      ...barSeries.map((s) => ({
        name: s.name,
        type: 'bar' as const,
        stack: stacked ? (s.stack || 'total') : undefined,
        itemStyle: { color: s.color },
        data: s.data,
        barMaxWidth: 40,
      })),
      ...lineSeries.map((s) => ({
        name: s.name,
        type: 'line' as const,
        yAxisIndex: s.yAxisIndex ?? 0,
        itemStyle: { color: s.color },
        lineStyle: { width: 2, color: s.color },
        symbol: 'circle',
        symbolSize: 6,
        data: s.data,
      })),
    ],
  }

  return <ReactECharts option={option} style={{ height }} />
}

export default ComboChart
