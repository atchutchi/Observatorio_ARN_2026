'use client'

import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

type LineSeries = {
  name: string
  data: number[]
  color: string
  areaStyle?: boolean
  smooth?: boolean
}

type LineChartProps = {
  categories: string[]
  series: LineSeries[]
  height?: number
  showLegend?: boolean
  yAxisLabel?: string
  formatValue?: (val: number) => string
}

const defaultFormat = (val: number) => {
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`
  return String(val)
}

const LineChart = ({
  categories,
  series,
  height = 350,
  showLegend = true,
  yAxisLabel,
  formatValue = defaultFormat,
}: LineChartProps) => {
  const option = {
    tooltip: { trigger: 'axis' as const },
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
      type: 'category' as const,
      data: categories,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value' as const,
      name: yAxisLabel,
      axisLabel: { formatter: formatValue },
    },
    series: series.map((s) => ({
      name: s.name,
      type: 'line' as const,
      data: s.data,
      itemStyle: { color: s.color },
      lineStyle: { width: 2, color: s.color },
      smooth: s.smooth ?? true,
      areaStyle: s.areaStyle ? { opacity: 0.15, color: s.color } : undefined,
      symbol: 'circle',
      symbolSize: 6,
    })),
  }

  return <ReactECharts option={option} style={{ height }} />
}

export default LineChart
