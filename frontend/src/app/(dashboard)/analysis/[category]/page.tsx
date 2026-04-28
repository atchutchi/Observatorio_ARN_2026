'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download } from 'lucide-react'
import { ChartWrapper, ComboChart, PieChart, LineChart } from '@/components/charts'
import api from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import toast from 'react-hot-toast'

type IndicatorDataItem = {
  indicator_code: string
  indicator_name: string
  indicator_level: number
  operator_code: string
  operator_name: string
  operator_color: string
  period: string
  value: number | null
  unit: string
  cumulative_type?: string
}

type RootIndicator = {
  code: string
  name: string
  unit: string
}

type MarketShareItem = {
  operator_code: string
  operator_name: string
  operator_color: string
  value: number
  share_pct: number
}

type TrendDataItem = {
  period: string
  total: number
  [key: string]: string | number
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

type OperatorInfo = { code: string; name: string; color: string }

const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2017 }, (_, i) => 2018 + i).reverse()

const CategoryAnalysisPage = () => {
  const params = useParams()
  const router = useRouter()
  const categoryCode = params.category as string

  const [year, setYear] = useState(CURRENT_YEAR)
  const [quarter, setQuarter] = useState<number | undefined>(undefined)
  const [categoryName, setCategoryName] = useState('')
  const [isCumulative, setIsCumulative] = useState(false)
  const [rootIndicators, setRootIndicators] = useState<RootIndicator[]>([])
  const [data, setData] = useState<IndicatorDataItem[]>([])
  const [trends, setTrends] = useState<TrendDataItem[]>([])
  const [trendOperators, setTrendOperators] = useState<OperatorInfo[]>([])
  const [marketShare, setMarketShare] = useState<MarketShareItem[]>([])
  const [growth, setGrowth] = useState<GrowthItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const qParams: Record<string, string | number> = { year }
      if (quarter) qParams.quarter = quarter

      const [indRes, trendRes, growthRes] = await Promise.all([
        api.get(`/dashboard/indicator/${categoryCode}/`, { params: qParams }),
        api.get('/dashboard/trends/', {
          params: { category: categoryCode, start_year: 2018, end_year: year },
        }),
        api.get('/dashboard/market-share/', {
          params: { ...qParams, market: categoryCode },
        }),
      ])

      setCategoryName(indRes.data.category?.name || categoryCode)
      setIsCumulative(indRes.data.category?.is_cumulative || false)
      setRootIndicators(indRes.data.root_indicators || [])
      setData(indRes.data.data || [])
      setTrends(trendRes.data.data || [])
      setTrendOperators(trendRes.data.operators || [])
      setMarketShare(growthRes.data.data || [])

      try {
        const gRes = await api.get('/dashboard/comparative/', {
          params: { year, categories: categoryCode },
        })
        const catGrowth = gRes.data.categories?.[categoryCode]?.growth || []
        setGrowth(catGrowth)
      } catch {
        setGrowth([])
      }
    } catch (err) {
      toast.error('Erro ao carregar dados da categoria')
    } finally {
      setIsLoading(false)
    }
  }, [categoryCode, year, quarter])

  useEffect(() => { fetchData() }, [fetchData])

  const handleExport = async () => {
    try {
      const response = await api.get('/dashboard/export/', {
        params: { category: categoryCode, year, format: 'xlsx' },
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${categoryCode}_${year}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch {
      toast.error('Erro ao exportar dados')
    }
  }

  const operatorCodes = Array.from(new Set(data.map((d) => d.operator_code)))
  const operators = operatorCodes.map((code) => {
    const item = data.find((d) => d.operator_code === code)
    return { code, name: item?.operator_name || code, color: item?.operator_color || '#6B7280' }
  })

  const groupedByIndicator = data.reduce<Record<string, IndicatorDataItem[]>>((acc, item) => {
    const key = item.indicator_code
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {})

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
            <h2 className="text-2xl font-bold text-gray-900">{categoryName}</h2>
            <p className="text-gray-500 text-sm mt-0.5">
              {isCumulative ? 'Dados cumulativos (3M/6M/9M/12M)' : 'Dados mensais/trimestrais'}
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
          {!isCumulative && (
            <select
              value={quarter ?? ''}
              onChange={(e) => setQuarter(e.target.value ? Number(e.target.value) : undefined)}
              className="input-field text-sm w-32"
              aria-label="Trimestre"
            >
              <option value="">Anual</option>
              <option value="1">Q1</option>
              <option value="2">Q2</option>
              <option value="3">Q3</option>
              <option value="4">Q4</option>
            </select>
          )}
          <button
            type="button"
            onClick={handleExport}
            className="btn-secondary text-sm flex items-center gap-2"
          >
            <Download className="w-4 h-4" /> Excel
          </button>
        </div>
      </div>

      {growth.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {growth.map((g) => (
            <div key={g.operator_code} className="card">
              <div className="flex items-center gap-3 mb-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: g.operator_color }}
                />
                <span className="font-medium text-gray-900 text-sm">{g.operator_name}</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(g.current_value)}</p>
              <p className={`text-sm font-medium mt-1 ${g.pct_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {g.pct_change >= 0 ? '+' : ''}{g.pct_change}% vs {year - 1}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartWrapper
            title={`Evolução — ${categoryName}`}
            subtitle={`2018 - ${year}`}
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
        </div>

        <ChartWrapper
          title="Quota de Mercado"
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

      <ChartWrapper
        title="Comparação entre Operadores"
        isLoading={isLoading}
        isEmpty={trends.length === 0}
      >
        <LineChart
          categories={trends.map((t) => t.period)}
          series={trendOperators.map((op) => ({
            name: op.name,
            data: trends.map((t) => (t[op.code] as number) || 0),
            color: op.color,
            areaStyle: true,
          }))}
        />
      </ChartWrapper>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-900">Dados Detalhados</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Indicador</th>
                {operators.map((op) => (
                  <th key={op.code} className="text-right py-3 px-4 font-semibold" style={{ color: op.color }}>
                    {op.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rootIndicators.map((ri) => {
                const indData = groupedByIndicator[ri.code] || []
                return (
                  <tr key={ri.code} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2.5 px-4 font-medium text-gray-900">{ri.name}</td>
                    {operators.map((op) => {
                      const entry = indData.find((d) => d.operator_code === op.code)
                      return (
                        <td key={op.code} className="text-right py-2.5 px-4 text-gray-700">
                          {entry?.value != null ? formatNumber(entry.value) : '—'}
                        </td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default CategoryAnalysisPage
