'use client'

import { useState, useCallback } from 'react'
import { useApi } from '@/hooks/use-api'
import { useAuthStore } from '@/lib/auth'
import api from '@/lib/api'
import { cn, formatNumber, getOperatorColor } from '@/lib/utils'
import toast from 'react-hot-toast'
import type { DataEntry } from '@/types'
import { CheckCircle, XCircle, AlertTriangle, Filter } from 'lucide-react'

const ValidationPage = () => {
  const user = useAuthStore((s) => s.user)
  const [filterOperator, setFilterOperator] = useState('')
  const [filterYear, setFilterYear] = useState<string>('')
  const [rejectComment, setRejectComment] = useState('')
  const [rejectingId, setRejectingId] = useState<number | null>(null)

  const params: Record<string, string | undefined> = {
    is_validated: 'false',
  }
  if (filterOperator) params['operator__code'] = filterOperator
  if (filterYear) params['period__year'] = filterYear

  const { data: pendingEntries, isLoading, refetch } = useApi<DataEntry[]>({
    url: '/data/pending_validation/',
    params,
  })

  const handleApprove = async (id: number) => {
    try {
      await api.post(`/data/${id}/validate_entry/`, { action: 'approve' })
      toast.success('Entrada aprovada')
      refetch()
    } catch {
      toast.error('Erro ao aprovar')
    }
  }

  const handleReject = async (id: number) => {
    try {
      await api.post(`/data/${id}/validate_entry/`, {
        action: 'reject',
        comment: rejectComment,
      })
      toast.success('Entrada rejeitada')
      setRejectingId(null)
      setRejectComment('')
      refetch()
    } catch {
      toast.error('Erro ao rejeitar')
    }
  }

  if (!user?.role || !['admin_arn', 'analyst_arn'].includes(user.role)) {
    return (
      <div className="card text-center py-12">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900">Acesso Restrito</h3>
        <p className="text-gray-500 mt-1">
          Apenas administradores e analistas ARN podem validar dados.
        </p>
      </div>
    )
  }

  const currentYears = Array.from({ length: 9 }, (_, i) => 2018 + i)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Validação de Dados</h2>
        <p className="text-gray-500 text-sm mt-1">
          Aprove ou rejeite dados submetidos pelos operadores
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            className="input-field max-w-xs"
            value={filterOperator}
            onChange={(e) => setFilterOperator(e.target.value)}
            aria-label="Filtrar por operador"
          >
            <option value="">Todos os operadores</option>
            <option value="TELECEL">Telecel</option>
            <option value="ORANGE">Orange</option>
            <option value="STARLINK">Starlink</option>
          </select>
          <select
            className="input-field max-w-xs"
            value={filterYear}
            onChange={(e) => setFilterYear(e.target.value)}
            aria-label="Filtrar por ano"
          >
            <option value="">Todos os anos</option>
            {currentYears.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="card text-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-arn-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">A carregar...</p>
        </div>
      ) : !pendingEntries?.length ? (
        <div className="card text-center py-12">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Tudo validado</h3>
          <p className="text-gray-500 mt-1">Não há entradas pendentes de validação.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Operador</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Indicador</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Período</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Valor</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Fonte</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">Acções</th>
              </tr>
            </thead>
            <tbody>
              {pendingEntries.map((entry) => (
                <tr key={entry.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span
                      className="inline-block w-2 h-2 rounded-full mr-2"
                      style={{ backgroundColor: getOperatorColor(entry.operator_code || '') }}
                    />
                    {entry.operator_code}
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-400 mr-1">{entry.indicator_code}</span>
                    {entry.indicator_name}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {entry.period_display}
                  </td>
                  <td className="py-3 px-4 text-right font-mono">
                    {formatNumber(entry.value)}
                  </td>
                  <td className="py-3 px-4">
                    <span className={cn(
                      'px-2 py-0.5 rounded text-xs font-medium',
                      entry.source === 'manual' && 'bg-blue-100 text-blue-700',
                      entry.source === 'upload' && 'bg-purple-100 text-purple-700',
                    )}>
                      {entry.source}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleApprove(entry.id)}
                        className="p-1.5 text-green-600 hover:bg-green-50 rounded-md transition-colors"
                        aria-label="Aprovar"
                      >
                        <CheckCircle className="w-5 h-5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setRejectingId(rejectingId === entry.id ? null : entry.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                        aria-label="Rejeitar"
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                    {rejectingId === entry.id && (
                      <div className="mt-2 space-y-2">
                        <input
                          type="text"
                          className="input-field text-xs"
                          placeholder="Motivo da rejeição..."
                          value={rejectComment}
                          onChange={(e) => setRejectComment(e.target.value)}
                        />
                        <button
                          type="button"
                          onClick={() => handleReject(entry.id)}
                          className="text-xs text-red-600 font-medium hover:underline"
                        >
                          Confirmar rejeição
                        </button>
                      </div>
                    )}
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

export default ValidationPage
