'use client'

import { useState, useEffect, useCallback } from 'react'
import Image from 'next/image'
import { TrendingUp, BarChart3, PieChart as PieChartIcon, Activity } from 'lucide-react'
import { ChartWrapper, PieChart, BarChart, LineChart, ComboChart } from '@/components/charts'
import KPICard from '@/components/ui/kpi-card'
import api from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import toast from 'react-hot-toast'

const OPERATOR_LOGOS: Record<string, string> = {
  ORANGE: '/logos/orange.png',
  TELECEL: '/logos/telecel.png',
}

const OperatorLogo = ({ code, color }: { code: string; color: string }) => {
  const logo = OPERATOR_LOGOS[code]
  if (logo) {
    return (
      <Image
        src={logo}
        alt={code}
        width={28}
        height={28}
        className="rounded-md object-contain"
      />
    )
  }
  return (
    <div className="w-7 h-7 rounded-md flex items-center justify-center text-white text-[10px] font-bold" style={{ backgroundColor: color }}>
      {code.slice(0, 2)}
    </div>
  )
}

type MarketShareItem = {
  operator_code: string
  operator_name: string
  operator_color: string
  value: number
  share_pct: number
}

type HHIData = {
  hhi: number
  classification: string
  operators: MarketShareItem[]
}

type GrowthItem = {
  operator_code: string
  operator_name: string
  operator_color: string
  current_value: number
  previous_value: number
  absolute_change: number
  pct_change: number
}

type TrendData = {
  period: string
  total: number
  [key: string]: string | number | undefined
}

type OperatorInfo = { code: string; name: string; color: string }

const MARKETS = [
  { key: 'mobile', label: 'Móvel (Assinantes)' },
  { key: 'voice', label: 'Voz (Tráfego)' },
  { key: 'sms', label: 'SMS' },
  { key: 'data', label: 'Dados' },
  { key: 'fixed_internet', label: 'Internet Fixo' },
  { key: 'revenue', label: 'Receitas' },
  { key: 'employment', label: 'Emprego' },
]

const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2017 }, (_, i) => 2018 + i).reverse()

const MarketAnalysisPage = () => {
  const [year, setYear] = useState(CURRENT_YEAR)
  const [market, setMarket] = useState('mobile')
  const [isLoading, setIsLoading] = useState(true)
  const [hhi, setHhi] = useState<HHIData | null>(null)
  const [growth, setGrowth] = useState<GrowthItem[]>([])
  const [trends, setTrends] = useState<TrendData[]>([])
  const [trendOperators, setTrendOperators] = useState<OperatorInfo[]>([])
  const [hhiHistory, setHhiHistory] = useState<{ year: number; hhi: number }[]>([])

  const marketCatMap: Record<string, string> = {
    mobile: 'estacoes_moveis',
    voice: 'trafego_originado',
    sms: 'trafego_originado',
    data: 'trafego_originado',
    fixed_internet: 'internet_fixo',
    revenue: 'receitas',
    employment: 'empregos',
  }

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const catCode = marketCatMap[market] || 'estacoes_moveis'

      const [hhiRes, growthRes, trendRes] = await Promise.all([
        api.get('/dashboard/hhi/', { params: { year, market } }),
        api.get('/dashboard/comparative/', { params: { year, categories: catCode } }),
        api.get('/dashboard/trends/', { params: { category: catCode, start_year: 2018, end_year: year } }),
      ])

      setHhi(hhiRes.data)
      setGrowth(growthRes.data?.growth_rates?.[catCode] || growthRes.data?.growth_rates || [])
      setTrends(trendRes.data.data || [])
      setTrendOperators(trendRes.data.operators || [])

      const hhiYears: { year: number; hhi: number }[] = []
      for (let y = 2018; y <= year; y++) {
        try {
          const r = await api.get('/dashboard/hhi/', { params: { year: y, market } })
          hhiYears.push({ year: y, hhi: r.data.hhi || 0 })
        } catch {
          hhiYears.push({ year: y, hhi: 0 })
        }
      }
      setHhiHistory(hhiYears)
    } catch {
      toast.error('Erro ao carregar dados de mercado')
    } finally {
      setIsLoading(false)
    }
  }, [year, market])

  useEffect(() => { fetchData() }, [fetchData])

  const hhiColor = !hhi ? '#6B7280'
    : hhi.hhi > 2500 ? '#EF4444'
    : hhi.hhi > 1500 ? '#F59E0B'
    : '#10B981'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Análise de Mercado</h2>
          <p className="text-gray-500 text-sm mt-1">Concentração, concorrência e evolução do mercado</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={market}
            onChange={(e) => setMarket(e.target.value)}
            className="input-field text-sm"
            aria-label="Seleccionar mercado"
          >
            {MARKETS.map((m) => (
              <option key={m.key} value={m.key}>{m.label}</option>
            ))}
          </select>
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
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard
          title="Índice HHI"
          value={hhi ? formatNumber(hhi.hhi) : '—'}
          icon={BarChart3}
          color={hhiColor}
        />
        <KPICard
          title="Classificação"
          value={hhi?.classification || '—'}
          icon={Activity}
          color={hhiColor}
        />
        <KPICard
          title="Operadores"
          value={hhi ? String(hhi.operators.length) : '—'}
          icon={PieChartIcon}
          color="#3B82F6"
        />
        <KPICard
          title="Líder de Mercado"
          value={hhi?.operators?.[0]?.operator_name || '—'}
          change={hhi?.operators?.[0] ? `${hhi.operators[0].share_pct}%` : undefined}
          changeType="positive"
          icon={TrendingUp}
          color="#8B5CF6"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartWrapper
          title="Quota de Mercado"
          subtitle={`${MARKETS.find((m) => m.key === market)?.label} — ${year}`}
          isLoading={isLoading}
          isEmpty={!hhi?.operators?.length}
        >
          <PieChart
            data={(hhi?.operators || []).map((s) => ({
              name: s.operator_name,
              value: s.value,
              color: s.operator_color,
            }))}
          />
        </ChartWrapper>

        <ChartWrapper
          title="Evolução HHI"
          subtitle={`2018 — ${year}`}
          isLoading={isLoading}
          isEmpty={hhiHistory.length === 0}
        >
          <LineChart
            categories={hhiHistory.map((h) => String(h.year))}
            series={[{
              name: 'HHI',
              data: hhiHistory.map((h) => h.hhi),
              color: '#1B2A4A',
            }]}
            yAxisLabel="HHI"
          />
        </ChartWrapper>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartWrapper
          title="Evolução por Operador"
          subtitle={`2018 — ${year}`}
          isLoading={isLoading}
          isEmpty={trends.length === 0}
        >
          <ComboChart
            categories={trends.map((t) => t.period)}
            barSeries={trendOperators.map((op) => ({
              name: op.name,
              data: trends.map((t) => (t[op.code] as number) || 0),
              color: op.color,
            }))}
            lineSeries={[{
              name: 'Total',
              data: trends.map((t) => t.total || 0),
              color: '#1B2A4A',
            }]}
            stacked
          />
        </ChartWrapper>

        <ChartWrapper
          title="Taxas de Crescimento"
          subtitle={`${year - 1} → ${year}`}
          isLoading={isLoading}
          isEmpty={growth.length === 0}
        >
          <BarChart
            categories={growth.map((g) => g.operator_name)}
            series={[{
              name: 'Crescimento (%)',
              data: growth.map((g) => g.pct_change),
              color: '#3B82F6',
            }]}
            yAxisLabel="%"
          />
        </ChartWrapper>
      </div>

      {hhi && hhi.operators.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Detalhe por Operador</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-left">
                  <th className="px-4 py-3 font-medium text-gray-500">Operador</th>
                  <th className="px-4 py-3 font-medium text-gray-500 text-right">Valor</th>
                  <th className="px-4 py-3 font-medium text-gray-500 text-right">Quota (%)</th>
                  <th className="px-4 py-3 font-medium text-gray-500">Quota Visual</th>
                </tr>
              </thead>
              <tbody>
                {hhi.operators.map((op) => (
                  <tr key={op.operator_code} className="border-b border-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <OperatorLogo code={op.operator_code} color={op.operator_color} />
                        <span className="font-medium text-gray-900">{op.operator_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-900 font-medium">{formatNumber(op.value)}</td>
                    <td className="px-4 py-3 text-right text-gray-900 font-bold">{op.share_pct}%</td>
                    <td className="px-4 py-3">
                      <div className="w-full bg-gray-100 rounded-full h-2.5">
                        <div
                          className="h-2.5 rounded-full transition-all"
                          style={{ width: `${op.share_pct}%`, backgroundColor: op.operator_color }}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="p-4 bg-gray-50 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">
                <strong>HHI = {formatNumber(hhi.hhi)}</strong> — {hhi.classification}
              </span>
              <span className="text-xs text-gray-400">
                HHI &lt; 1500: Competitivo | 1500-2500: Moderado | &gt; 2500: Concentrado
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MarketAnalysisPage
