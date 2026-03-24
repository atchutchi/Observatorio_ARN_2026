'use client'

import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

type PieDataItem = {
  name: string
  value: number
  color: string
}

type PieChartProps = {
  data: PieDataItem[]
  height?: number
  donut?: boolean
  showLegend?: boolean
  showLabel?: boolean
}

const PieChart = ({
  data,
  height = 350,
  donut = true,
  showLegend = true,
  showLabel = true,
}: PieChartProps) => {
  const option = {
    tooltip: {
      trigger: 'item' as const,
      formatter: '{b}: {c} ({d}%)',
    },
    legend: showLegend ? { bottom: 0 } : undefined,
    series: [
      {
        type: 'pie' as const,
        radius: donut ? ['40%', '70%'] : ['0%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: donut ? 8 : 4,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: showLabel
          ? { show: true, formatter: '{b}: {d}%' }
          : { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
        },
        data: data.map((d) => ({
          name: d.name,
          value: d.value,
          itemStyle: { color: d.color },
        })),
      },
    ],
  }

  return <ReactECharts option={option} style={{ height }} />
}

export default PieChart
