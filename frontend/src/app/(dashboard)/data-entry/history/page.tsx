'use client'

import { useState } from 'react'
import { useApi } from '@/hooks/use-api'
import { useAuthStore } from '@/lib/auth'
import { cn, formatNumber, getOperatorColor } from '@/lib/utils'
import type { DataEntry } from '@/types'
import { History, Filter, CheckCircle, Clock, XCircle } from 'lucide-react'

const HistoryPage = () => {
  const user = useAuthStore((s) => s.user)
  const [filterYear, setFilterYear] = useState<string>('')
  const [filterSource, setFilterSource] = useState<string>('')
  const [filterValidated, setFilterValidated] = useState<string>('')
  const [filterCategory, setFilterCategory] = useState<string>('')

  const params: Record<string, string | undefined> = {}
  if (filterYear) params['period__year'] = filterYear
  if (filterSource) params['source'] = filterSource
  if (filterValidated) params['is_validated'] = filterValidated
  if (filterCategory) params['indicator__category__code'] = filterCategory

  const { data: entries, isLoading } = useApi<DataEntry[]>({
    url: '/data/',
    params,
  })

  const currentYears = Array.from({ length: 9 }, (_, i) => 2018 + i)
  const categories = [
    { code: 'estacoes_moveis', name: 'Estações Móveis' },
    { code: 'trafego_originado', name: 'Tráfego Originado' },
    { code: 'trafego_terminado', name: 'Tráfego Terminado' },
    { code: 'trafego_roaming', name: 'Roaming Internacional' },
    { code: 'lbi', name: 'LBI' },
    { code: 'internet_fixo', name: 'Internet Fixo' },
    { code: 'internet_trafic', name: 'Internet Traffic' },
    { code: 'tarifario_voz', name: 'Tarifário de Voz' },
    { code: 'receitas', name: 'Receitas' },
    { code: 'empregos', name: 'Empregos' },
    { code: 'investimento', name: 'Investimento' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Histórico de Dados</h2>
        <p className="text-gray-500 text-sm mt-1">
          {user?.is_arn_staff
            ? 'Todos os dados submetidos por todos os operadores'
            : 'Dados submetidos pelo seu operador'
          }
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="w-5 h-5 text-gray-400 shrink-0" />

          <select
            className="input-field max-w-[180px]"
            value={filterYear}
            onChange={(e) => setFilterYear(e.target.value)}
            aria-label="Filtrar por ano"
          >
            <option value="">Todos os anos</option>
            {currentYears.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <select
            className="input-field max-w-[200px]"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            aria-label="Filtrar por indicador"
          >
            <option value="">Todos os indicadores</option>
            {categories.map((c) => (
              <option key={c.code} value={c.code}>{c.name}</option>
            ))}
          </select>

          <select
            className="input-field max-w-[150px]"
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            aria-label="Filtrar por fonte"
          >
            <option value="">Todas as fontes</option>
            <option value="manual">Manual</option>
            <option value="upload">Upload</option>
            <option value="calculated">Calculado</option>
            <option value="imported">Importado</option>
          </select>

          <select
            className="input-field max-w-[150px]"
            value={filterValidated}
            onChange={(e) => setFilterValidated(e.target.value)}
            aria-label="Filtrar por validação"
          >
            <option value="">Todos os estados</option>
            <option value="true">Validado</option>
            <option value="false">Pendente</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="card text-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-arn-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">A carregar...</p>
        </div>
      ) : !entries?.length ? (
        <div className="card text-center py-12">
          <History className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Sem dados</h3>
          <p className="text-gray-500 mt-1">Nenhuma entrada encontrada com os filtros actuais.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <div className="mb-3 text-sm text-gray-500">
            {entries.length} {entries.length === 1 ? 'registo' : 'registos'} encontrados
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Operador</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Indicador</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Período</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Valor</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">Fonte</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">Estado</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Data</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span
                      className="inline-block w-2 h-2 rounded-full mr-2"
                      style={{ backgroundColor: getOperatorColor((entry as any).operator_code || '') }}
                    />
                    {(entry as any).operator_code}
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-400 mr-1 text-xs">{(entry as any).indicator_code}</span>
                    <span className="text-gray-700">{(entry as any).indicator_name}</span>
                  </td>
                  <td className="py-3 px-4 text-gray-600 text-xs">
                    {(entry as any).period_display}
                  </td>
                  <td className="py-3 px-4 text-right font-mono">
                    {formatNumber(entry.value)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={cn(
                      'px-2 py-0.5 rounded text-xs font-medium',
                      entry.source === 'manual' && 'bg-blue-100 text-blue-700',
                      entry.source === 'upload' && 'bg-purple-100 text-purple-700',
                      entry.source === 'calculated' && 'bg-gray-100 text-gray-700',
                      entry.source === 'imported' && 'bg-amber-100 text-amber-700',
                    )}>
                      {entry.source}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {entry.is_validated ? (
                      <CheckCircle className="w-4 h-4 text-green-500 mx-auto" />
                    ) : (
                      <Clock className="w-4 h-4 text-amber-500 mx-auto" />
                    )}
                  </td>
                  <td className="py-3 px-4 text-xs text-gray-500">
                    {new Date(entry.submitted_at).toLocaleDateString('pt-PT')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default HistoryPage
