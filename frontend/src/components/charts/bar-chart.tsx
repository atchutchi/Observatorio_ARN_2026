'use client'

import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

type BarSeries = {
  name: string
  data: number[]
  color: string
  stack?: string
}

type BarChartProps = {
  categories: string[]
  series: BarSeries[]
  height?: number
  stacked?: boolean
  horizontal?: boolean
  showLegend?: boolean
  yAxisLabel?: string
  formatValue?: (val: number) => string
}

const defaultFormat = (val: number) => {
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`
  return String(val)
}

const BarChart = ({
  categories,
  series,
  height = 350,
  stacked = false,
  horizontal = false,
  showLegend = true,
  yAxisLabel,
  formatValue = defaultFormat,
}: BarChartProps) => {
  const option = {
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'shadow' as const },
    },
    legend: showLegend
      ? { data: series.map((s) => s.name), bottom: 0 }
      : undefined,
    grid: {
      left: '3%',
      right: '4%',
      bottom: showLegend ? '15%' : '5%',
      top: yAxisLabel ? '12%' : '5%',
      containLabel: true,
    },
    xAxis: {
      type: horizontal ? ('value' as const) : ('category' as const),
      data: horizontal ? undefined : categories,
      axisLabel: horizontal ? { formatter: formatValue } : { rotate: categories.length > 8 ? 45 : 0 },
    },
    yAxis: {
      type: horizontal ? ('category' as const) : ('value' as const),
      data: horizontal ? categories : undefined,
      name: yAxisLabel,
      axisLabel: horizontal ? undefined : { formatter: formatValue },
    },
    series: series.map((s) => ({
      name: s.name,
      type: 'bar' as const,
      stack: stacked ? (s.stack || 'total') : undefined,
      itemStyle: { color: s.color },
      data: s.data,
      barMaxWidth: 40,
    })),
  }

  return <ReactECharts option={option} style={{ height }} />
}

export default BarChart
