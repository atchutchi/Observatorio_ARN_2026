'use client'

import { useState, useEffect, useCallback } from 'react'
import { ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { ChartWrapper, BarChart, PieChart } from '@/components/charts'
import api from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import toast from 'react-hot-toast'

type HHIData = {
  hhi: number
  classification: string
  operators: { operator_code: string; operator_name: string; operator_color: string; value: number; share_pct: number }[]
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

const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2017 }, (_, i) => 2018 + i).reverse()

const MARKETS = [
  { value: 'mobile', label: 'Mercado Móvel' },
  { value: 'voice', label: 'Tráfego de Voz' },
  { value: 'sms', label: 'SMS' },
  { value: 'data', label: 'Tráfego de Dados' },
  { value: 'fixed_internet', label: 'Internet Fixa' },
  { value: 'revenue', label: 'Receitas' },
  { value: 'employment', label: 'Emprego' },
]

const ComparativeAnalysisPage = () => {
  const router = useRouter()
  const [year, setYear] = useState(CURRENT_YEAR)
  const [market, setMarket] = useState('mobile')
  const [hhi, setHHI] = useState<HHIData | null>(null)
  const [growth, setGrowth] = useState<GrowthItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const hhiRes = await api.get('/dashboard/hhi/', { params: { year, market } })
      setHHI(hhiRes.data)

      const marketCategoryMap: Record<string, string> = {
        mobile: 'estacoes_moveis',
        voice: 'trafego_originado',
        sms: 'trafego_originado',
        data: 'trafego_originado',
        fixed_internet: 'internet_fixo',
        revenue: 'receitas',
        employment: 'empregos',
      }
      const catCode = marketCategoryMap[market] || 'estacoes_moveis'

      try {
        const gRes = await api.get('/dashboard/comparative/', {
          params: { year, categories: catCode },
        })
        setGrowth(gRes.data.categories?.[catCode]?.growth || [])
      } catch {
        setGrowth([])
      }
    } catch {
      toast.error('Erro ao carregar dados comparativos')
    } finally {
      setIsLoading(false)
    }
  }, [year, market])

  useEffect(() => { fetchData() }, [fetchData])

  const hhiColor = hhi
    ? hhi.hhi > 2500 ? '#E74C3C' : hhi.hhi > 1500 ? '#F39C12' : '#2ECC71'
    : '#6B7280'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => router.push('/analysis')}
            className="p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Voltar"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Análise Comparativa</h2>
            <p className="text-gray-500 text-sm mt-0.5">
              Concentração de mercado, quotas e crescimento por operador
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="input-field text-sm w-28"
            aria-label="Ano"
          >
            {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
          <select
            value={market}
            onChange={(e) => setMarket(e.target.value)}
            className="input-field text-sm w-44"
            aria-label="Mercado"
          >
            {MARKETS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
      </div>

      {hhi && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <p className="text-sm text-gray-500 mb-1">Índice HHI</p>
            <p className="text-4xl font-bold" style={{ color: hhiColor }}>
              {formatNumber(hhi.hhi)}
            </p>
            <p className="text-sm mt-2 font-medium" style={{ color: hhiColor }}>
              {hhi.classification}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-sm text-gray-500 mb-1">Operadores no Mercado</p>
            <p className="text-4xl font-bold text-gray-900">{hhi.operators.length}</p>
            <p className="text-sm text-gray-500 mt-2">operadores activos</p>
          </div>
          <div className="card text-center">
            <p className="text-sm text-gray-500 mb-1">Líder de Mercado</p>
            {hhi.operators[0] && (
              <>
                <p className="text-2xl font-bold" style={{ color: hhi.operators[0].operator_color }}>
                  {hhi.operators[0].operator_name}
                </p>
                <p className="text-sm text-gray-500 mt-2">{hhi.operators[0].share_pct}% do mercado</p>
              </>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartWrapper
          title="Quota de Mercado"
          subtitle={MARKETS.find((m) => m.value === market)?.label}
          isLoading={isLoading}
          isEmpty={!hhi || hhi.operators.length === 0}
        >
          <PieChart
            data={(hhi?.operators || []).map((op) => ({
              name: op.operator_name,
              value: op.value,
              color: op.operator_color,
            }))}
          />
        </ChartWrapper>

        <ChartWrapper
          title="Crescimento Anual por Operador"
          subtitle={`${year} vs ${year - 1}`}
          isLoading={isLoading}
          isEmpty={growth.length === 0}
        >
          <BarChart
            categories={growth.map((g) => g.operator_name)}
            series={[{
              name: 'Crescimento %',
              data: growth.map((g) => g.pct_change),
              color: '#1B2A4A',
            }]}
            yAxisLabel="%"
          />
        </ChartWrapper>
      </div>

      {growth.length > 0 && (
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Detalhes de Crescimento</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Operador</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">{year - 1}</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">{year}</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Variação</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">%</th>
                </tr>
              </thead>
              <tbody>
                {growth.map((g) => (
                  <tr key={g.operator_code} className="border-b border-gray-100">
                    <td className="py-2.5 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: g.operator_color }} />
                        <span className="font-medium">{g.operator_name}</span>
                      </div>
                    </td>
                    <td className="text-right py-2.5 px-4">{formatNumber(g.previous_value)}</td>
                    <td className="text-right py-2.5 px-4 font-medium">{formatNumber(g.current_value)}</td>
                    <td className="text-right py-2.5 px-4">{formatNumber(g.absolute_change)}</td>
                    <td className={`text-right py-2.5 px-4 font-medium ${g.pct_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {g.pct_change >= 0 ? '+' : ''}{g.pct_change}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default ComparativeAnalysisPage
