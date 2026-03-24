'use client'

import { useState, useEffect, useCallback } from 'react'
import { Users, DollarSign, Wifi, TrendingUp, BarChart3, Activity } from 'lucide-react'
import KPICard from '@/components/ui/kpi-card'
import { ChartWrapper, ComboChart, PieChart, BarChart } from '@/components/charts'
import api from '@/lib/api'
import { formatNumber } from '@/lib/utils'

type SummaryData = {
  total_subscribers: number
  total_revenue: number
  total_data_traffic: number
  penetration_rate: number
  subscriber_change: number
  active_operators: number
}

type TrendData = {
  period: string
  total: number
  TELECEL?: number
  ORANGE?: number
  STARLINK?: number
  [key: string]: string | number | undefined
}

type MarketShareItem = {
  operator_code: string
  operator_name: string
  operator_color: string
  value: number
  share_pct: number
}

type OperatorInfo = {
  code: string
  name: string
  color: string
}

const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2017 }, (_, i) => 2018 + i).reverse()

const DashboardPage = () => {
  const [year, setYear] = useState(CURRENT_YEAR)
  const [quarter, setQuarter] = useState<number | undefined>(undefined)
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [trendOperators, setTrendOperators] = useState<OperatorInfo[]>([])
  const [marketShare, setMarketShare] = useState<MarketShareItem[]>([])
  const [revenueTrends, setRevenueTrends] = useState<TrendData[]>([])
  const [revenueOperators, setRevenueOperators] = useState<OperatorInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true)
    try {
      const params: Record<string, number> = { year }
      if (quarter) params.quarter = quarter

      const [sumRes, trendRes, shareRes, revRes] = await Promise.all([
        api.get('/dashboard/summary/', { params }),
        api.get('/dashboard/trends/', { params: { category: 'estacoes_moveis', start_year: 2018, end_year: year } }),
        api.get('/dashboard/market-share/', { params: { ...params, market: 'mobile' } }),
        api.get('/dashboard/trends/', { params: { category: 'receitas', indicator: '8', start_year: 2018, end_year: year } }),
      ])

      setSummary(sumRes.data)
      setTrends(trendRes.data.data || [])
      setTrendOperators(trendRes.data.operators || [])
      setMarketShare(shareRes.data.data || [])
      setRevenueTrends(revRes.data.data || [])
      setRevenueOperators(revRes.data.operators || [])
    } catch {
      // API may return empty when no data exists
    } finally {
      setIsLoading(false)
    }
  }, [year, quarter])

  useEffect(() => { fetchDashboard() }, [fetchDashboard])

  const formatLargeNumber = (val: number) => {
    if (!val) return '0'
    if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(2)}M`
    if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`
    return formatNumber(val)
  }

  const trendCategories = trends.map((t) => t.period)
  const buildBarSeries = (operators: OperatorInfo[], data: TrendData[]) =>
    operators.map((op) => ({
      name: op.name,
      data: data.map((t) => (t[op.code] as number) || 0),
      color: op.color,
    }))
  const buildLineSeries = (data: TrendData[]) => [{
    name: 'Total',
    data: data.map((t) => t.total || 0),
    color: '#1B2A4A',
  }]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-500 text-sm mt-1">Panorama geral do mercado de telecomunicações</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="input-field text-sm w-28"
            aria-label="Seleccionar ano"
          >
            {YEARS.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select
            value={quarter ?? ''}
            onChange={(e) => setQuarter(e.target.value ? Number(e.target.value) : undefined)}
            className="input-field text-sm w-32"
            aria-label="Seleccionar trimestre"
          >
            <option value="">Anual</option>
            <option value="1">Q1 (Jan-Mar)</option>
            <option value="2">Q2 (Abr-Jun)</option>
            <option value="3">Q3 (Jul-Set)</option>
            <option value="4">Q4 (Out-Dez)</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Assinantes Móvel"
          value={summary ? formatLargeNumber(summary.total_subscribers) : '—'}
          change={summary ? `${summary.subscriber_change > 0 ? '+' : ''}${summary.subscriber_change}% vs ${year - 1}` : undefined}
          changeType={summary && summary.subscriber_change >= 0 ? 'positive' : 'negative'}
          icon={Users}
          color="#1B2A4A"
        />
        <KPICard
          title="Volume de Negócios"
          value={summary ? `${formatLargeNumber(summary.total_revenue)} FCFA` : '—'}
          icon={DollarSign}
          color="#2ECC71"
        />
        <KPICard
          title="Tráfego de Dados"
          value={summary ? formatLargeNumber(summary.total_data_traffic) : '—'}
          icon={Wifi}
          color="#3498DB"
        />
        <KPICard
          title="Taxa de Penetração"
          value={summary ? `${summary.penetration_rate}%` : '—'}
          icon={TrendingUp}
          color="#9B59B6"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartWrapper
            title="Evolução do Parque de Assinantes"
            subtitle={`2018 - ${year}`}
            isLoading={isLoading}
            isEmpty={trends.length === 0}
          >
            <ComboChart
              categories={trendCategories}
              barSeries={buildBarSeries(trendOperators, trends)}
              lineSeries={buildLineSeries(trends)}
              stacked
              yAxisLabel="Assinantes"
            />
          </ChartWrapper>
        </div>

        <ChartWrapper
          title="Quota de Mercado Móvel"
          subtitle={`${year}${quarter ? ` Q${quarter}` : ''}`}
          isLoading={isLoading}
          isEmpty={marketShare.length === 0}
        >
          <PieChart
            data={marketShare.map((s) => ({
              name: s.operator_name,
              value: s.value,
              color: s.operator_color,
            }))}
          />
        </ChartWrapper>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartWrapper
          title="Evolução das Receitas"
          subtitle={`Volume de Negócios (Milhões FCFA) — 2018-${year}`}
          isLoading={isLoading}
          isEmpty={revenueTrends.length === 0}
        >
          <BarChart
            categories={revenueTrends.map((t) => t.period)}
            series={buildBarSeries(revenueOperators, revenueTrends)}
            stacked
            yAxisLabel="M FCFA"
          />
        </ChartWrapper>

        <ChartWrapper
          title="Operadores Activos"
          subtitle={`${summary?.active_operators || 0} operadores no mercado`}
          isLoading={isLoading}
          isEmpty={!summary}
        >
          <div className="grid grid-cols-1 gap-4 py-4">
            {trendOperators.map((op) => {
              const share = marketShare.find((s) => s.operator_code === op.code)
              return (
                <div key={op.code} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-white text-xs font-bold"
                    style={{ backgroundColor: op.color }}
                  >
                    {op.code.substring(0, 3)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{op.name}</p>
                    <p className="text-sm text-gray-500">
                      {share ? `Quota: ${share.share_pct}%` : 'Sem dados'}
                    </p>
                  </div>
                  {share && (
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{formatLargeNumber(share.value)}</p>
                      <p className="text-xs text-gray-500">assinantes</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </ChartWrapper>
      </div>
    </div>
  )
}

export default DashboardPage
