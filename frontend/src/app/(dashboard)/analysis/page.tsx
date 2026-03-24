'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  Users, Phone, PhoneIncoming, Globe, Wifi, Monitor,
  Activity, CreditCard, Briefcase, Building2, BarChart3,
} from 'lucide-react'
import api from '@/lib/api'

type Category = {
  id: number
  code: string
  name: string
  description: string
  order: number
  is_cumulative: boolean
  indicator_count?: number
}

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  estacoes_moveis: Users,
  trafego_originado: Phone,
  trafego_terminado: PhoneIncoming,
  trafego_roaming: Globe,
  lbi: Wifi,
  internet_fixo: Monitor,
  internet_trafic: Activity,
  tarifario_voz: CreditCard,
  receitas: Briefcase,
  empregos: Building2,
  investimento: BarChart3,
}

const CATEGORY_COLORS: Record<string, string> = {
  estacoes_moveis: '#1B2A4A',
  trafego_originado: '#E30613',
  trafego_terminado: '#FF6600',
  trafego_roaming: '#9B59B6',
  lbi: '#3498DB',
  internet_fixo: '#2ECC71',
  internet_trafic: '#1ABC9C',
  tarifario_voz: '#E67E22',
  receitas: '#27AE60',
  empregos: '#8E44AD',
  investimento: '#2C3E50',
}

const AnalysisIndexPage = () => {
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await api.get('/indicator-categories/')
        setCategories(res.data.results ?? res.data)
      } catch {
        // fallback empty
      } finally {
        setIsLoading(false)
      }
    }
    fetchCategories()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Análise por Indicador</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 11 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-32" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Análise por Indicador</h2>
        <p className="text-gray-500 text-sm mt-1">
          Seleccione uma categoria para ver dados detalhados, gráficos e comparações
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((cat) => {
          const Icon = CATEGORY_ICONS[cat.code] || BarChart3
          const color = CATEGORY_COLORS[cat.code] || '#6B7280'

          return (
            <Link
              key={cat.code}
              href={`/analysis/${cat.code}`}
              className="card hover:shadow-lg transition-shadow group cursor-pointer"
            >
              <div className="flex items-start gap-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                  style={{ backgroundColor: `${color}15` }}
                >
                  <Icon className="w-6 h-6" style={{ color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 text-sm group-hover:text-arn-primary transition-colors">
                    {cat.name}
                  </h3>
                  {cat.description && (
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{cat.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    {cat.is_cumulative && (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full">
                        Cumulativo
                      </span>
                    )}
                    <span className="text-xs text-gray-400">
                      {cat.order}º indicador
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="card bg-arn-primary/5 border border-arn-primary/20">
        <Link href="/analysis/comparative" className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-arn-primary flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-arn-primary">Análise Comparativa</h3>
            <p className="text-sm text-gray-600">
              Compare indicadores entre operadores, analise concentração de mercado (HHI) e tendências multi-anuais
            </p>
          </div>
        </Link>
      </div>
    </div>
  )
}

export default AnalysisIndexPage
