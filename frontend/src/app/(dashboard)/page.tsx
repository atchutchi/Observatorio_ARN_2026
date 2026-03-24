'use client'

import dynamic from 'next/dynamic'
import { Users, DollarSign, Wifi, TrendingUp } from 'lucide-react'
import KPICard from '@/components/ui/kpi-card'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

const MOCK_SUBSCRIBER_DATA = {
  years: ['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
  telecel: [980000, 1020000, 1050000, 1100000, 1150000, 1200000, 1280000],
  orange: [850000, 900000, 950000, 980000, 1020000, 1080000, 1120000],
}

const subscriberChartOption = {
  tooltip: { trigger: 'axis' as const },
  legend: { data: ['Telecel', 'Orange', 'Total'], bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category' as const, data: MOCK_SUBSCRIBER_DATA.years },
  yAxis: {
    type: 'value' as const,
    axisLabel: {
      formatter: (val: number) => {
        if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `${(val / 1000).toFixed(0)}K`
        return String(val)
      },
    },
  },
  series: [
    {
      name: 'Telecel',
      type: 'bar' as const,
      stack: 'total',
      itemStyle: { color: '#E30613' },
      data: MOCK_SUBSCRIBER_DATA.telecel,
    },
    {
      name: 'Orange',
      type: 'bar' as const,
      stack: 'total',
      itemStyle: { color: '#FF6600' },
      data: MOCK_SUBSCRIBER_DATA.orange,
    },
    {
      name: 'Total',
      type: 'line' as const,
      itemStyle: { color: '#1B2A4A' },
      lineStyle: { width: 2 },
      data: MOCK_SUBSCRIBER_DATA.telecel.map((v, i) => v + MOCK_SUBSCRIBER_DATA.orange[i]),
    },
  ],
}

const marketShareOption = {
  tooltip: { trigger: 'item' as const },
  legend: { bottom: 0 },
  series: [
    {
      name: 'Quota de Mercado',
      type: 'pie' as const,
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {d}%' },
      data: [
        { value: 1280000, name: 'Telecel', itemStyle: { color: '#E30613' } },
        { value: 1120000, name: 'Orange', itemStyle: { color: '#FF6600' } },
      ],
    },
  ],
}

const DashboardPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">Panorama geral do mercado de telecomunicações</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Assinantes Móvel"
          value="2,40M"
          change="+5.2% vs 2023"
          changeType="positive"
          icon={Users}
          color="#1B2A4A"
        />
        <KPICard
          title="Volume de Negócios"
          value="48,3 Mil M FCFA"
          change="+3.8% vs 2023"
          changeType="positive"
          icon={DollarSign}
          color="#2ECC71"
        />
        <KPICard
          title="Tráfego Dados"
          value="12,5 TB"
          change="+28.4% vs 2023"
          changeType="positive"
          icon={Wifi}
          color="#3498DB"
        />
        <KPICard
          title="Taxa de Penetração"
          value="115,9%"
          change="+4.1 pp vs 2023"
          changeType="positive"
          icon={TrendingUp}
          color="#9B59B6"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Evolução do Parque de Assinantes (2018-2024)
          </h3>
          <ReactECharts option={subscriberChartOption} style={{ height: 350 }} />
        </div>

        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            Quota de Mercado Móvel
          </h3>
          <ReactECharts option={marketShareOption} style={{ height: 350 }} />
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
