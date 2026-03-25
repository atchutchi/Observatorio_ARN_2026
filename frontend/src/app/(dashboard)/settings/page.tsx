'use client'

import { useState, useCallback, useEffect } from 'react'
import Link from 'next/link'
import {
  Settings, Users, Building2, BarChart3, Loader2, Plus, Pencil,
  Trash2, X, ChevronRight, Activity, Shield,
} from 'lucide-react'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/auth'
import toast from 'react-hot-toast'
import type { OperatorListItem, IndicatorCategory } from '@/types'

type Tab = 'overview' | 'operators' | 'categories'

const SettingsPage = () => {
  const user = useAuthStore((s) => s.user)
  const [tab, setTab] = useState<Tab>('overview')
  const [operators, setOperators] = useState<OperatorListItem[]>([])
  const [categories, setCategories] = useState<IndicatorCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState({ users: 0, periods: 0, entries: 0 })

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [opsRes, catsRes, usersRes, periodsRes] = await Promise.all([
        api.get('/operators/'),
        api.get('/indicator-categories/'),
        api.get('/users/'),
        api.get('/periods/'),
      ])
      setOperators(opsRes.data.results ?? opsRes.data)
      setCategories(catsRes.data.results ?? catsRes.data)

      const usersData = usersRes.data.results ?? usersRes.data
      const periodsData = periodsRes.data.results ?? periodsRes.data
      setStats({
        users: Array.isArray(usersData) ? usersData.length : usersRes.data.count || 0,
        periods: Array.isArray(periodsData) ? periodsData.length : periodsRes.data.count || 0,
        entries: 0,
      })
    } catch {
      toast.error('Erro ao carregar configurações')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  if (user?.role !== 'admin_arn') {
    return (
      <div className="text-center py-16">
        <Shield className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900">Acesso Restrito</h2>
        <p className="text-gray-500 mt-2">Apenas administradores ARN podem aceder a esta página.</p>
      </div>
    )
  }

  const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
    { id: 'overview', label: 'Visão Geral', icon: Settings },
    { id: 'operators', label: 'Operadores', icon: Building2 },
    { id: 'categories', label: 'Categorias', icon: BarChart3 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Configurações</h2>
        <p className="text-gray-500 text-sm mt-1">Administração do sistema</p>
      </div>

      <div className="flex gap-2 border-b border-gray-200">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id
                ? 'border-arn-primary text-arn-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-arn-primary" />
        </div>
      ) : (
        <>
          {tab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link href="/settings/users" className="card p-6 hover:shadow-md transition-shadow group">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-3">
                        <Users className="w-6 h-6 text-blue-600" />
                      </div>
                      <h3 className="font-semibold text-gray-900">Utilizadores</h3>
                      <p className="text-2xl font-bold text-gray-900 mt-1">{stats.users}</p>
                      <p className="text-xs text-gray-500 mt-1">Gerir contas e permissões</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-gray-500 transition-colors" />
                  </div>
                </Link>

                <div className="card p-6">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-3">
                    <Building2 className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">Operadores</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{operators.length}</p>
                  <p className="text-xs text-gray-500 mt-1">Operadores registados no sistema</p>
                </div>

                <div className="card p-6">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-3">
                    <BarChart3 className="w-6 h-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">Categorias</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{categories.length}</p>
                  <p className="text-xs text-gray-500 mt-1">Categorias de indicadores</p>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Acções Rápidas</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Link href="/settings/users" className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <Users className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Gestão de Utilizadores</p>
                      <p className="text-xs text-gray-500">Criar, editar e remover utilizadores</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                  </Link>
                  <Link href="/reports/generate" className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <Activity className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Gerar Relatório</p>
                      <p className="text-xs text-gray-500">Relatório trimestral ou anual</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                  </Link>
                </div>
              </div>
            </div>
          )}

          {tab === 'operators' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Operadores ({operators.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-left">
                      <th className="px-4 py-3 font-medium text-gray-500">Operador</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Código</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Tipo</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {operators.map((op) => (
                      <tr key={op.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div
                              className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                              style={{ backgroundColor: op.brand_color || '#6B7280' }}
                            >
                              {op.code.substring(0, 2)}
                            </div>
                            <span className="font-medium text-gray-900">{op.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-600 font-mono text-xs">{op.code}</td>
                        <td className="px-4 py-3 text-gray-600">{op.operator_type_code}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${op.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {op.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === 'categories' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Categorias de Indicadores ({categories.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-left">
                      <th className="px-4 py-3 font-medium text-gray-500">#</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Nome</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Código</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Indicadores</th>
                      <th className="px-4 py-3 font-medium text-gray-500">Tipo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map((cat) => (
                      <tr key={cat.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                        <td className="px-4 py-3 text-gray-400">{cat.order}</td>
                        <td className="px-4 py-3 font-medium text-gray-900">{cat.name}</td>
                        <td className="px-4 py-3 text-gray-600 font-mono text-xs">{cat.code}</td>
                        <td className="px-4 py-3 text-gray-600">{cat.indicator_count ?? '—'}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${cat.is_cumulative ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}`}>
                            {cat.is_cumulative ? 'Cumulativo' : 'Mensal'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SettingsPage
